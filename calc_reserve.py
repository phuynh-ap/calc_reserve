# calc_reserve.py
#
#   Calculates NS spinning reserve.
#
#   - Needs to be run in the GUI.
#   - Run a powerflow solve before running the script.
#   - Ensure the dMachType dictionary has all machine buses you'd like to check
#     for reserve.
#   - Output appears in progress window.
#
#   Be aware this doesn't check topology past the generator bus but powerflow
#   should identify islands.
#
#   I'm also not 100% confident everything is captured so please be skeptical.
#
#
#   Revisions:
#   2023/04/27  PVH
#   Initial release.
#

# ---- Start of imports -------------------------------------------------------
# System imports start here
import os, sys
import socket

# ---- Initialize program settings for PSSE run outside of GUI ----------------
nameWstn        = "EMA1902003L"                                 # Workstation name
locPsseDef      = "C:\Program Files (x86)\pti\psse34\PSSPY27"   # Install path
nameHost        = socket.gethostname()


# Add  PSSEBIN dir, if it's the server, use the server path
if nameHost == nameWstn:
    PSSE_LOCATION = locPsseDef
    # Include Peter's tools path
    #sys.path.append('c:/work/resources/planning/psse/psse_api')
else:
    PSSE_LOCATION = locPsseDef
    # Include Peter's tools path
    #sys.path.append('h:/work/resources/planning/psse/psse_api')

sys.path.append(PSSE_LOCATION)
os.environ['PATH'] = os.environ['PATH'] + ';' +  PSSE_LOCATION

import psse34
import psspy

psspy.throwPsseExceptions = True
# ---- Resuming imports -------------------------------------------------------
# ---- End of   imports -------------------------------------------------------

# ---- Start of global definitions --------------------------------------------
# In the format:
# - Machine name (key)
# - Machine bus (int)
# - Machine ID (str)
# - Machine type (str)
dMachType = {   "88S-LINGAN_1" :    [199001, "1", "Thermal"],
                "88S-LINGAN_2" :    [199002, "2", "Thermal"],
                "88S-LINGAN_3" :    [199003, "3", "Thermal"],
                "88S-LINGAN_4" :    [199004, "4", "Thermal"],
                "VJ_GEN1" :         [199027, "1", "CT"],
                "VJ_GEN2" :         [199028, "2", "CT"],
                "85S-WRECK_1" :     [199036, "1", "Hydro"],
                "85S-WRECK_2" :     [199037, "2", "Hydro"],
                "89S-ACONI" :       [199043, "1", "Thermal"],
                "1C-TUPPER_GN" :    [199055, "2", "Thermal"],
                "47C-NP_TMP1" :     [199061, "1", "Load"],
                "47C-NP_TMP2" :     [199062, "2", "Load"],
                "47C-NP_TMP3" :     [199064, "3", "Load"],
                "48C-BIOMASS" :     [199072, "1", "Thermal"],
                "24C-GEN" :         [199081, "1", "Hydro"],
                "IR8-SABLE" :       [199083, "1", "Wind"],
                "50N-TRENTON5" :    [199085, "5", "Thermal"],
                "50N-TRENTON6" :    [199086, "6", "Thermal"],
                "95H-MALAY_FL" :    [199097, "1", "Hydro"],
                "96H-GEN1" :        [199099, "1", "Hydro"],
                "96H-GEN2" :        [199099, "2", "Hydro"],
                "96H-GEN3" :        [199099, "3", "Hydro"],
                "53N-NRTPULP" :     [199105, "1", "Thermal"],
                "91H-TUFTSCV6" :    [199164, "6", "CT"],
                "91H-TUFTCV1" :     [199167, "1", "Thermal"],
                "91H-TUFTCV2" :     [199168, "2", "Thermal"],
                "91H-TUFTCV3" :     [199169, "3", "Thermal"],
                "91H-TUFTS4" :      [199181, "4", "CT"],
                "91H-TUFTS5" :      [199182, "5", "CT"],
                "14H-BURNS1" :      [199188, "1", "CT"],
                "14H-BURNS2" :      [199188, "2", "CT"],
                "14H-BURNS3" :      [199189, "3", "CT"],
                "14H-BURNS4" :      [199189, "4", "CT"],
                "92/3/4H-GEN" :     [199226, "1", "Hydro"],
                "5W-DEEP_BRK" :     [199247, "1", "Hydro"],
                "6W-COWIE_FL" :     [199248, "1", "Hydro"],
                "4W-L_GR_BRK" :     [199250, "1", "Hydro"],
                "3W-BIG_FALL" :     [199253, "1", "Hydro"],
                "1W-UP_LAKE" :      [199255, "1", "Hydro"],
                "2W-LOW_LAKE" :     [199256, "1", "Hydro"],
                "104W-BROOKLY" :    [199279, "N", "Thermal"],
                "9W-TUSKT_HY" :     [199285, "1", "Hydro"],
                "10W-TUSK_CT" :     [199289, "1", "CT"],
                "2V-AVON2HYD" :     [199305, "2", "Hydro"],
                "1V-AVON1HYD" :     [199306, "1", "Hydro"],
                "8V-SALMON_HY" :    [199316, "1", "Hydro"],
                "9V-CROIX_HY" :     [199317, "1", "Hydro"],
                "3V-HELS_GATE1" :   [199327, "1", "Hydro"],
                "3V-HELS_GATE2" :   [199327, "2", "Hydro"],
                "4V-WHITE_ROC" :    [199328, "1", "Hydro"],
                "5V-LUMSDEN" :      [199330, "1", "Hydro"],
                "6V-HOLLOW_B" :     [199331, "1", "Hydro"],
                "7V-METHALS" :      [199334, "1", "Hydro"],
                "12V-LEQUILLE" :    [199349, "1", "Hydro"],
                "81V-TIDAL" :       [199353, "1", "Tidal"],
                "11V-PARADISE" :    [199357, "1", "Hydro"],
                "10V-NICTAUX" :     [199361, "1", "Hydro"],
                "14V-RIDGE_HY" :    [199368, "1", "Hydro"],
                "15V-SISSIBOO" :    [199371, "1", "Hydro"],
                "13V-GEN" :         [199372, "1", "Hydro"],
                "91V-FOURTH_L" :    [199373, "1", "Hydro"],
                "16V-GEN1" :        [199375, "1", "Hydro"],
                "16V-GEN2" :        [199375, "2", "Hydro"],
                "106W-PUB_WND" :    [199401, "1", "Wind"],
                "109S-LINWIND" :    [199423, "1", "Wind"],
                "110W-OFFWF" :      [199504, "1", "Wind"],
                "110W-MBPPW" :      [199510, "1", "Wind"],
                "92N-AMHSTGEN" :    [199533, "1", "Wind"],
                "IR516-SMEC" :      [199557, "1", "Tidal"],
                "IR517-VACANT" :    [199558, "1", "Tidal"],
                "IR542-MINAS" :     [199559, "1", "Tidal"],
                "89N_NUTBG" :       [199584, "1", "Wind"],
                "91N-DALHOGEN" :    [199593, "1", "Wind"],
                "93N-GLENDHU" :     [199613, "1", "Wind"],
                "102V-GEN_BUS" :    [199638, "1", "Wind"],
                "120C-BEARHD" :     [199692, "1", "Wind"],
                "98V-GULLCOVE" :    [199712, "1", "Wind"],
                "IR597_GEN" :       [199728, "1", "Wind"],
                "IR574_G" :         [199804, "1", "Wind"],
                "301NS-DC-P1" :     [199855, "1", "HVDC"],
                "301NS-DC-P2" :     [199857, "1", "HVDC"]
        }
# ---- End of   global definitions --------------------------------------------

# ---- Start of main() --------------------------------------------------------
def runmain():
    iReserve = 0

    print("Bus/ID        PGen    PMax Reserve Name")
    for mKey, mVal in dMachType.items():
        if( (mVal[2] == "Thermal") or (mVal[2] == "CT") or (mVal[2] == "Hydro") ):
            # Get machine status
            iErr, mStat = psspy.macint( ibus    = mVal[0],
                                        id      = mVal[1],
                                        string  = "STATUS"
                                        )
            # Get machine bus status
            iErr, bStat = psspy.busint( ibus    = mVal[0],
                                        string  = "TYPE"
                                        )

            if( (mStat) and (bStat != -2) and (bStat != 4) ):
                # Get machine pgen
                iErr, pGen = psspy.macdat(  ibus    = mVal[0],
                                            id      = mVal[1],
                                            string  = "P"
                                            )
                # Get machine pmax
                iErr, pMax = psspy.macdat(  ibus    = mVal[0],
                                            id      = mVal[1],
                                            string  = "PMAX"
                                            )

                iReserve = iReserve + pMax - pGen

                print("{:<10s}".format(str(mVal[0]) + mVal[1]) + "{:>8.2f}".format(pGen) + "{:>8.2f}".format(pMax) + "{:>8.2f}".format(pMax - pGen) + " " + mKey)

            #else:
            #    print("Offline " + str(mVal[0]) + ":" + mVal[1] + " " + mKey)

    print("\n")
    print("-----------------------------------------------")
    print("Total system reserve is: " + "{:.2f}".format(iReserve) + " MW.")


if __name__ == "__main__":
    runmain()
# ---- End of main() ----------------------------------------------------------