import datetime
from io import BytesIO

import matplotlib
import numpy as np

from covid_micro.app import get_cached

matplotlib.use('Agg')

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib

ZEIT_KREISE_URL = "https://interactive.zeit.de/cronjobs/2020/corona/germany.json"

zeit_kreise_key = {"1001": {"ags": "1001", "name": "Flensburg", "lat": 54.785, "lon": 9.439, "population": 89504, "bundesland": "Schleswig-Holstein"},
                   "1002": {"ags": "1002", "name": "Kiel", "lat": 54.325, "lon": 10.133, "population": 247548, "bundesland": "Schleswig-Holstein"},
                   "1003": {"ags": "1003", "name": "Lübeck", "lat": 53.872, "lon": 10.727, "population": 217198, "bundesland": "Schleswig-Holstein"},
                   "1004": {"ags": "1004", "name": "Neumünster", "lat": 54.081, "lon": 9.984, "population": 79487, "bundesland": "Schleswig-Holstein"},
                   "1051": {"ags": "1051", "name": "Dithmarschen", "lat": 54.134, "lon": 9.108, "population": 133210, "bundesland": "Schleswig-Holstein"},
                   "1053": {"ags": "1053", "name": "Herzogtum Lauenburg", "lat": 53.589, "lon": 10.602, "population": 197264, "bundesland": "Schleswig-Holstein"},
                   "1054": {"ags": "1054", "name": "Nordfriesland", "lat": 54.615, "lon": 8.899, "population": 165507, "bundesland": "Schleswig-Holstein"},
                   "1055": {"ags": "1055", "name": "Ostholstein", "lat": 54.189, "lon": 10.819, "population": 200581, "bundesland": "Schleswig-Holstein"},
                   "1056": {"ags": "1056", "name": "Pinneberg", "lat": 53.717, "lon": 9.746, "population": 314391, "bundesland": "Schleswig-Holstein"},
                   "1057": {"ags": "1057", "name": "Plön", "lat": 54.243, "lon": 10.363, "population": 128647, "bundesland": "Schleswig-Holstein"},
                   "1058": {"ags": "1058", "name": "Rendsburg-Eckernförde", "lat": 54.289, "lon": 9.781, "population": 272775, "bundesland": "Schleswig-Holstein"},
                   "1059": {"ags": "1059", "name": "Schleswig-Flensburg", "lat": 54.624, "lon": 9.504, "population": 200025, "bundesland": "Schleswig-Holstein"},
                   "1060": {"ags": "1060", "name": "Segeberg", "lat": 53.92, "lon": 10.141, "population": 276032, "bundesland": "Schleswig-Holstein"},
                   "1061": {"ags": "1061", "name": "Steinburg", "lat": 53.929, "lon": 9.519, "population": 131347, "bundesland": "Schleswig-Holstein"},
                   "1062": {"ags": "1062", "name": "Stormarn", "lat": 53.721, "lon": 10.332, "population": 243196, "bundesland": "Schleswig-Holstein"},
                   "2000": {"ags": "2000", "name": "Hamburg", "lat": 53.546, "lon": 10.021, "population": 1841179, "bundesland": "Hamburg"},
                   "3101": {"ags": "3101", "name": "Braunschweig", "lat": 52.276, "lon": 10.524, "population": 248292, "bundesland": "Niedersachsen"},
                   "3102": {"ags": "3102", "name": "Salzgitter", "lat": 52.126, "lon": 10.371, "population": 104948, "bundesland": "Niedersachsen"},
                   "3103": {"ags": "3103", "name": "Wolfsburg", "lat": 52.41, "lon": 10.785, "population": 124151, "bundesland": "Niedersachsen"},
                   "3151": {"ags": "3151", "name": "Gifhorn", "lat": 52.58, "lon": 10.604, "population": 175920, "bundesland": "Niedersachsen"},
                   "3153": {"ags": "3153", "name": "Goslar", "lat": 51.875, "lon": 10.4, "population": 137014, "bundesland": "Niedersachsen"},
                   "3154": {"ags": "3154", "name": "Helmstedt", "lat": 52.26, "lon": 10.89, "population": 91307, "bundesland": "Niedersachsen"},
                   "3155": {"ags": "3155", "name": "Northeim", "lat": 51.742, "lon": 9.848, "population": 132765, "bundesland": "Niedersachsen"},
                   "3157": {"ags": "3157", "name": "Peine", "lat": 52.304, "lon": 10.256, "population": 133965, "bundesland": "Niedersachsen"},
                   "3158": {"ags": "3158", "name": "Wolfenbüttel", "lat": 52.127, "lon": 10.584, "population": 119960, "bundesland": "Niedersachsen"},
                   "3159": {"ags": "3159", "name": "Göttingen", "lat": 51.564, "lon": 10.089, "population": 328074, "bundesland": "Niedersachsen"},
                   "3241": {"ags": "3241", "name": "Region Hannover", "lat": 52.422, "lon": 9.72, "population": 1157624, "bundesland": "Niedersachsen"},
                   "3251": {"ags": "3251", "name": "Diepholz", "lat": 52.728, "lon": 8.702, "population": 216886, "bundesland": "Niedersachsen"},
                   "3252": {"ags": "3252", "name": "Hameln-Pyrmont", "lat": 52.095, "lon": 9.389, "population": 148559, "bundesland": "Niedersachsen"},
                   "3254": {"ags": "3254", "name": "Hildesheim", "lat": 52.09, "lon": 9.944, "population": 276594, "bundesland": "Niedersachsen"},
                   "3255": {"ags": "3255", "name": "Holzminden", "lat": 51.881, "lon": 9.552, "population": 70975, "bundesland": "Niedersachsen"},
                   "3256": {"ags": "3256", "name": "Nienburg (Weser)", "lat": 52.609, "lon": 9.115, "population": 121386, "bundesland": "Niedersachsen"},
                   "3257": {"ags": "3257", "name": "Schaumburg", "lat": 52.293, "lon": 9.207, "population": 157781, "bundesland": "Niedersachsen"},
                   "3351": {"ags": "3351", "name": "Celle", "lat": 52.714, "lon": 10.104, "population": 178936, "bundesland": "Niedersachsen"},
                   "3352": {"ags": "3352", "name": "Cuxhaven", "lat": 53.617, "lon": 8.812, "population": 198213, "bundesland": "Niedersachsen"},
                   "3353": {"ags": "3353", "name": "Harburg", "lat": 53.316, "lon": 9.962, "population": 252776, "bundesland": "Niedersachsen"},
                   "3354": {"ags": "3354", "name": "Lüchow-Dannenberg", "lat": 53.02, "lon": 11.123, "population": 48424, "bundesland": "Niedersachsen"},
                   "3355": {"ags": "3355", "name": "Lüneburg", "lat": 53.233, "lon": 10.573, "population": 183372, "bundesland": "Niedersachsen"},
                   "3356": {"ags": "3356", "name": "Osterholz", "lat": 53.251, "lon": 8.808, "population": 113517, "bundesland": "Niedersachsen"},
                   "3357": {"ags": "3357", "name": "Rotenburg (Wümme)", "lat": 53.25, "lon": 9.307, "population": 163455, "bundesland": "Niedersachsen"},
                   "3358": {"ags": "3358", "name": "Heidekreis", "lat": 52.929, "lon": 9.77, "population": 139755, "bundesland": "Niedersachsen"},
                   "3359": {"ags": "3359", "name": "Stade", "lat": 53.578, "lon": 9.419, "population": 203102, "bundesland": "Niedersachsen"},
                   "3360": {"ags": "3360", "name": "Uelzen", "lat": 52.983, "lon": 10.547, "population": 92572, "bundesland": "Niedersachsen"},
                   "3361": {"ags": "3361", "name": "Verden", "lat": 52.973, "lon": 9.176, "population": 136792, "bundesland": "Niedersachsen"},
                   "3401": {"ags": "3401", "name": "Delmenhorst", "lat": 53.05, "lon": 8.646, "population": 77607, "bundesland": "Niedersachsen"},
                   "3402": {"ags": "3402", "name": "Emden", "lat": 53.361, "lon": 7.182, "population": 50195, "bundesland": "Niedersachsen"},
                   "3403": {"ags": "3403", "name": "Oldenburg", "lat": 52.988, "lon": 8.39, "population": 168210, "bundesland": "Niedersachsen"},
                   "3404": {"ags": "3404", "name": "Osnabrück", "lat": 52.278, "lon": 8.047, "population": 164748, "bundesland": "Niedersachsen"},
                   "3405": {"ags": "3405", "name": "Wilhelmshaven", "lat": 53.567, "lon": 8.087, "population": 76278, "bundesland": "Niedersachsen"},
                   "3451": {"ags": "3451", "name": "Ammerland", "lat": 53.218, "lon": 8.013, "population": 124071, "bundesland": "Niedersachsen"},
                   "3452": {"ags": "3452", "name": "Aurich", "lat": 53.496, "lon": 7.37, "population": 189848, "bundesland": "Niedersachsen"},
                   "3453": {"ags": "3453", "name": "Cloppenburg", "lat": 52.911, "lon": 7.905, "population": 169348, "bundesland": "Niedersachsen"},
                   "3454": {"ags": "3454", "name": "Emsland", "lat": 52.738, "lon": 7.403, "population": 325657, "bundesland": "Niedersachsen"},
                   "3455": {"ags": "3455", "name": "Friesland", "lat": 53.509, "lon": 7.983, "population": 98460, "bundesland": "Niedersachsen"},
                   "3456": {"ags": "3456", "name": "Grafschaft Bentheim", "lat": 52.476, "lon": 7.02, "population": 136511, "bundesland": "Niedersachsen"},
                   "3457": {"ags": "3457", "name": "Leer", "lat": 53.241, "lon": 7.478, "population": 169809, "bundesland": "Niedersachsen"},
                   "3458": {"ags": "3458", "name": "Oldenburg (Oldb)", "lat": 53.145, "lon": 8.225, "population": 130144, "bundesland": "Niedersachsen"},
                   "3459": {"ags": "3459", "name": "Osnabrück (Landkreis)", "lat": 52.382, "lon": 8.045, "population": 357343, "bundesland": "Niedersachsen"},
                   "3460": {"ags": "3460", "name": "Vechta", "lat": 52.661, "lon": 8.223, "population": 141598, "bundesland": "Niedersachsen"},
                   "3461": {"ags": "3461", "name": "Wesermarsch", "lat": 53.356, "lon": 8.39, "population": 88624, "bundesland": "Niedersachsen"},
                   "3462": {"ags": "3462", "name": "Wittmund", "lat": 53.575, "lon": 7.705, "population": 56882, "bundesland": "Niedersachsen"},
                   "4011": {"ags": "4011", "name": "Bremen", "lat": 53.118, "lon": 8.781, "population": 569352, "bundesland": "Bremen"},
                   "4012": {"ags": "4012", "name": "Bremerhaven", "lat": 53.537, "lon": 8.586, "population": 113634, "bundesland": "Bremen"},
                   "5111": {"ags": "5111", "name": "Düsseldorf", "lat": 51.234, "lon": 6.81, "population": 619294, "bundesland": "Nordrhein-Westfalen"},
                   "5112": {"ags": "5112", "name": "Duisburg", "lat": 51.439, "lon": 6.735, "population": 498590, "bundesland": "Nordrhein-Westfalen"},
                   "5113": {"ags": "5113", "name": "Essen", "lat": 51.433, "lon": 7.017, "population": 583109, "bundesland": "Nordrhein-Westfalen"},
                   "5114": {"ags": "5114", "name": "Krefeld", "lat": 51.345, "lon": 6.578, "population": 227020, "bundesland": "Nordrhein-Westfalen"},
                   "5116": {"ags": "5116", "name": "Mönchengladbach", "lat": 51.167, "lon": 6.411, "population": 261454, "bundesland": "Nordrhein-Westfalen"},
                   "5117": {"ags": "5117", "name": "Mülheim an der Ruhr", "lat": 51.414, "lon": 6.879, "population": 170880, "bundesland": "Nordrhein-Westfalen"},
                   "5119": {"ags": "5119", "name": "Oberhausen", "lat": 51.512, "lon": 6.847, "population": 210829, "bundesland": "Nordrhein-Westfalen"},
                   "5120": {"ags": "5120", "name": "Remscheid", "lat": 51.183, "lon": 7.224, "population": 110994, "bundesland": "Nordrhein-Westfalen"},
                   "5122": {"ags": "5122", "name": "Solingen", "lat": 51.162, "lon": 7.067, "population": 159360, "bundesland": "Nordrhein-Westfalen"},
                   "5124": {"ags": "5124", "name": "Wuppertal", "lat": 51.251, "lon": 7.168, "population": 354382, "bundesland": "Nordrhein-Westfalen"},
                   "5154": {"ags": "5154", "name": "Kleve", "lat": 51.652, "lon": 6.259, "population": 310974, "bundesland": "Nordrhein-Westfalen"},
                   "5158": {"ags": "5158", "name": "Mettmann", "lat": 51.257, "lon": 6.969, "population": 485684, "bundesland": "Nordrhein-Westfalen"},
                   "5162": {"ags": "5162", "name": "Rhein-Kreis Neuss", "lat": 51.144, "lon": 6.648, "population": 451007, "bundesland": "Nordrhein-Westfalen"},
                   "5166": {"ags": "5166", "name": "Viersen", "lat": 51.283, "lon": 6.325, "population": 298935, "bundesland": "Nordrhein-Westfalen"},
                   "5170": {"ags": "5170", "name": "Wesel", "lat": 51.626, "lon": 6.619, "population": 459809, "bundesland": "Nordrhein-Westfalen"},
                   "5314": {"ags": "5314", "name": "Bonn", "lat": 50.706, "lon": 7.11, "population": 327258, "bundesland": "Nordrhein-Westfalen"},
                   "5315": {"ags": "5315", "name": "Köln", "lat": 50.945, "lon": 6.973, "population": 1085664, "bundesland": "Nordrhein-Westfalen"},
                   "5316": {"ags": "5316", "name": "Leverkusen", "lat": 51.053, "lon": 7.016, "population": 163838, "bundesland": "Nordrhein-Westfalen"},
                   "5334": {"ags": "5334", "name": "Städteregion Aachen", "lat": 50.728, "lon": 6.218, "population": 555465, "bundesland": "Nordrhein-Westfalen"},
                   "5358": {"ags": "5358", "name": "Düren", "lat": 50.818, "lon": 6.445, "population": 263722, "bundesland": "Nordrhein-Westfalen"},
                   "5362": {"ags": "5362", "name": "Rhein-Erft-Kreis", "lat": 50.905, "lon": 6.716, "population": 470089, "bundesland": "Nordrhein-Westfalen"},
                   "5366": {"ags": "5366", "name": "Euskirchen", "lat": 50.537, "lon": 6.644, "population": 192840, "bundesland": "Nordrhein-Westfalen"},
                   "5370": {"ags": "5370", "name": "Heinsberg", "lat": 51.05, "lon": 6.165, "population": 254322, "bundesland": "Nordrhein-Westfalen"},
                   "5374": {"ags": "5374", "name": "Oberbergischer Kreis", "lat": 51.013, "lon": 7.517, "population": 272471, "bundesland": "Nordrhein-Westfalen"},
                   "5378": {"ags": "5378", "name": "Rheinisch-Bergischer Kreis", "lat": 51.023, "lon": 7.195, "population": 283455, "bundesland": "Nordrhein-Westfalen"},
                   "5382": {"ags": "5382", "name": "Rhein-Sieg-Kreis", "lat": 50.761, "lon": 7.234, "population": 599780, "bundesland": "Nordrhein-Westfalen"},
                   "5512": {"ags": "5512", "name": "Bottrop", "lat": 51.571, "lon": 6.919, "population": 117383, "bundesland": "Nordrhein-Westfalen"},
                   "5513": {"ags": "5513", "name": "Gelsenkirchen", "lat": 51.553, "lon": 7.072, "population": 260654, "bundesland": "Nordrhein-Westfalen"},
                   "5515": {"ags": "5515", "name": "Münster", "lat": 51.955, "lon": 7.624, "population": 314319, "bundesland": "Nordrhein-Westfalen"},
                   "5554": {"ags": "5554", "name": "Borken", "lat": 51.961, "lon": 6.899, "population": 370676, "bundesland": "Nordrhein-Westfalen"},
                   "5558": {"ags": "5558", "name": "Coesfeld", "lat": 51.867, "lon": 7.366, "population": 219929, "bundesland": "Nordrhein-Westfalen"},
                   "5562": {"ags": "5562", "name": "Recklinghausen", "lat": 51.672, "lon": 7.159, "population": 615261, "bundesland": "Nordrhein-Westfalen"},
                   "5566": {"ags": "5566", "name": "Steinfurt", "lat": 52.212, "lon": 7.579, "population": 447614, "bundesland": "Nordrhein-Westfalen"},
                   "5570": {"ags": "5570", "name": "Warendorf", "lat": 51.87, "lon": 7.959, "population": 277783, "bundesland": "Nordrhein-Westfalen"},
                   "5711": {"ags": "5711", "name": "Bielefeld", "lat": 52.011, "lon": 8.542, "population": 333786, "bundesland": "Nordrhein-Westfalen"},
                   "5754": {"ags": "5754", "name": "Gütersloh", "lat": 51.932, "lon": 8.352, "population": 364083, "bundesland": "Nordrhein-Westfalen"},
                   "5758": {"ags": "5758", "name": "Herford", "lat": 52.168, "lon": 8.644, "population": 250783, "bundesland": "Nordrhein-Westfalen"},
                   "5762": {"ags": "5762", "name": "Höxter", "lat": 51.685, "lon": 9.178, "population": 140667, "bundesland": "Nordrhein-Westfalen"},
                   "5766": {"ags": "5766", "name": "Lippe", "lat": 51.981, "lon": 8.951, "population": 348391, "bundesland": "Nordrhein-Westfalen"},
                   "5770": {"ags": "5770", "name": "Minden-Lübbecke", "lat": 52.352, "lon": 8.74, "population": 310710, "bundesland": "Nordrhein-Westfalen"},
                   "5774": {"ags": "5774", "name": "Paderborn", "lat": 51.664, "lon": 8.719, "population": 306890, "bundesland": "Nordrhein-Westfalen"},
                   "5911": {"ags": "5911", "name": "Bochum", "lat": 51.47, "lon": 7.226, "population": 364628, "bundesland": "Nordrhein-Westfalen"},
                   "5913": {"ags": "5913", "name": "Dortmund", "lat": 51.516, "lon": 7.476, "population": 587010, "bundesland": "Nordrhein-Westfalen"},
                   "5914": {"ags": "5914", "name": "Hagen", "lat": 51.348, "lon": 7.499, "population": 188814, "bundesland": "Nordrhein-Westfalen"},
                   "5915": {"ags": "5915", "name": "Hamm", "lat": 51.665, "lon": 7.823, "population": 179111, "bundesland": "Nordrhein-Westfalen"},
                   "5916": {"ags": "5916", "name": "Herne", "lat": 51.537, "lon": 7.207, "population": 156374, "bundesland": "Nordrhein-Westfalen"},
                   "5954": {"ags": "5954", "name": "Ennepe-Ruhr-Kreis", "lat": 51.347, "lon": 7.324, "population": 324296, "bundesland": "Nordrhein-Westfalen"},
                   "5958": {"ags": "5958", "name": "Hochsauerlandkreis", "lat": 51.307, "lon": 8.385, "population": 260475, "bundesland": "Nordrhein-Westfalen"},
                   "5962": {"ags": "5962", "name": "Märkischer Kreis", "lat": 51.263, "lon": 7.713, "population": 412120, "bundesland": "Nordrhein-Westfalen"},
                   "5966": {"ags": "5966", "name": "Olpe", "lat": 51.086, "lon": 7.977, "population": 134775, "bundesland": "Nordrhein-Westfalen"},
                   "5970": {"ags": "5970", "name": "Siegen-Wittgenstein", "lat": 50.938, "lon": 8.196, "population": 278210, "bundesland": "Nordrhein-Westfalen"},
                   "5974": {"ags": "5974", "name": "Soest", "lat": 51.564, "lon": 8.217, "population": 301902, "bundesland": "Nordrhein-Westfalen"},
                   "5978": {"ags": "5978", "name": "Unna", "lat": 51.579, "lon": 7.637, "population": 394782, "bundesland": "Nordrhein-Westfalen"},
                   "6411": {"ags": "6411", "name": "Darmstadt", "lat": 49.882, "lon": 8.664, "population": 159207, "bundesland": "Hessen"},
                   "6412": {"ags": "6412", "name": "Frankfurt am Main", "lat": 50.118, "lon": 8.645, "population": 753056, "bundesland": "Hessen"},
                   "6413": {"ags": "6413", "name": "Offenbach am Main", "lat": 50.091, "lon": 8.782, "population": 128744, "bundesland": "Hessen"},
                   "6414": {"ags": "6414", "name": "Wiesbaden", "lat": 50.079, "lon": 8.262, "population": 278342, "bundesland": "Hessen"},
                   "6431": {"ags": "6431", "name": "Bergstraße", "lat": 49.617, "lon": 8.66, "population": 269694, "bundesland": "Hessen"},
                   "6432": {"ags": "6432", "name": "Darmstadt-Dieburg", "lat": 49.856, "lon": 8.796, "population": 297399, "bundesland": "Hessen"},
                   "6433": {"ags": "6433", "name": "Groß-Gerau", "lat": 49.905, "lon": 8.47, "population": 274526, "bundesland": "Hessen"},
                   "6434": {"ags": "6434", "name": "Hochtaunuskreis", "lat": 50.281, "lon": 8.504, "population": 236564, "bundesland": "Hessen"},
                   "6435": {"ags": "6435", "name": "Main-Kinzig-Kreis", "lat": 50.244, "lon": 9.286, "population": 418950, "bundesland": "Hessen"},
                   "6436": {"ags": "6436", "name": "Main-Taunus-Kreis", "lat": 50.102, "lon": 8.435, "population": 237735, "bundesland": "Hessen"},
                   "6437": {"ags": "6437", "name": "Odenwaldkreis", "lat": 49.67, "lon": 8.979, "population": 96798, "bundesland": "Hessen"},
                   "6438": {"ags": "6438", "name": "Offenbach", "lat": 50.021, "lon": 8.811, "population": 354092, "bundesland": "Hessen"},
                   "6439": {"ags": "6439", "name": "Rheingau-Taunus-Kreis", "lat": 50.142, "lon": 8.081, "population": 187157, "bundesland": "Hessen"},
                   "6440": {"ags": "6440", "name": "Wetteraukreis", "lat": 50.355, "lon": 8.907, "population": 306460, "bundesland": "Hessen"},
                   "6531": {"ags": "6531", "name": "Gießen", "lat": 50.57, "lon": 8.808, "population": 268876, "bundesland": "Hessen"},
                   "6532": {"ags": "6532", "name": "Lahn-Dill-Kreis", "lat": 50.648, "lon": 8.365, "population": 253777, "bundesland": "Hessen"},
                   "6533": {"ags": "6533", "name": "Limburg-Weilburg", "lat": 50.427, "lon": 8.199, "population": 172083, "bundesland": "Hessen"},
                   "6534": {"ags": "6534", "name": "Marburg-Biedenkopf", "lat": 50.836, "lon": 8.738, "population": 246648, "bundesland": "Hessen"},
                   "6535": {"ags": "6535", "name": "Vogelsbergkreis", "lat": 50.638, "lon": 9.271, "population": 105878, "bundesland": "Hessen"},
                   "6611": {"ags": "6611", "name": "Kassel", "lat": 51.31, "lon": 9.459, "population": 201585, "bundesland": "Hessen"},
                   "6631": {"ags": "6631", "name": "Fulda", "lat": 50.564, "lon": 9.759, "population": 222584, "bundesland": "Hessen"},
                   "6632": {"ags": "6632", "name": "Hersfeld-Rotenburg", "lat": 50.906, "lon": 9.753, "population": 120829, "bundesland": "Hessen"},
                   "6633": {"ags": "6633", "name": "Kassel (Landkreis)", "lat": 51.401, "lon": 9.406, "population": 236633, "bundesland": "Hessen"},
                   "6634": {"ags": "6634", "name": "Schwalm-Eder-Kreis", "lat": 51.024, "lon": 9.374, "population": 180222, "bundesland": "Hessen"},
                   "6635": {"ags": "6635", "name": "Waldeck-Frankenberg", "lat": 51.19, "lon": 8.889, "population": 156953, "bundesland": "Hessen"},
                   "6636": {"ags": "6636", "name": "Werra-Meißner-Kreis", "lat": 51.191, "lon": 9.93, "population": 101017, "bundesland": "Hessen"},
                   "7111": {"ags": "7111", "name": "Koblenz", "lat": 50.349, "lon": 7.579, "population": 114024, "bundesland": "Rheinland-Pfalz"},
                   "7131": {"ags": "7131", "name": "Ahrweiler", "lat": 50.468, "lon": 7.046, "population": 129727, "bundesland": "Rheinland-Pfalz"},
                   "7132": {"ags": "7132", "name": "Altenkirchen (Westerwald)", "lat": 50.751, "lon": 7.744, "population": 128705, "bundesland": "Rheinland-Pfalz"},
                   "7133": {"ags": "7133", "name": "Bad Kreuznach", "lat": 49.824, "lon": 7.686, "population": 158080, "bundesland": "Rheinland-Pfalz"},
                   "7134": {"ags": "7134", "name": "Birkenfeld", "lat": 49.713, "lon": 7.278, "population": 80720, "bundesland": "Rheinland-Pfalz"},
                   "7135": {"ags": "7135", "name": "Cochem-Zell", "lat": 50.133, "lon": 7.174, "population": 61587, "bundesland": "Rheinland-Pfalz"},
                   "7137": {"ags": "7137", "name": "Mayen-Koblenz", "lat": 50.331, "lon": 7.331, "population": 214259, "bundesland": "Rheinland-Pfalz"},
                   "7138": {"ags": "7138", "name": "Neuwied", "lat": 50.558, "lon": 7.468, "population": 181941, "bundesland": "Rheinland-Pfalz"},
                   "7140": {"ags": "7140", "name": "Rhein-Hunsrück-Kreis", "lat": 50.044, "lon": 7.5, "population": 102937, "bundesland": "Rheinland-Pfalz"},
                   "7141": {"ags": "7141", "name": "Rhein-Lahn-Kreis", "lat": 50.263, "lon": 7.842, "population": 122308, "bundesland": "Rheinland-Pfalz"},
                   "7143": {"ags": "7143", "name": "Westerwaldkreis", "lat": 50.552, "lon": 7.865, "population": 201597, "bundesland": "Rheinland-Pfalz"},
                   "7211": {"ags": "7211", "name": "Trier", "lat": 49.763, "lon": 6.655, "population": 110636, "bundesland": "Rheinland-Pfalz"},
                   "7231": {"ags": "7231", "name": "Bernkastel-Wittlich", "lat": 49.925, "lon": 6.967, "population": 112262, "bundesland": "Rheinland-Pfalz"},
                   "7232": {"ags": "7232", "name": "Eifelkreis Bitburg-Prüm", "lat": 50.063, "lon": 6.41, "population": 98561, "bundesland": "Rheinland-Pfalz"},
                   "7233": {"ags": "7233", "name": "Vulkaneifel", "lat": 50.239, "lon": 6.747, "population": 60603, "bundesland": "Rheinland-Pfalz"},
                   "7235": {"ags": "7235", "name": "Trier-Saarburg", "lat": 49.697, "lon": 6.695, "population": 148945, "bundesland": "Rheinland-Pfalz"},
                   "7311": {"ags": "7311", "name": "Frankenthal (Pfalz)", "lat": 49.533, "lon": 8.358, "population": 48561, "bundesland": "Rheinland-Pfalz"},
                   "7312": {"ags": "7312", "name": "Kaiserslautern", "lat": 49.434, "lon": 7.761, "population": 99845, "bundesland": "Rheinland-Pfalz"},
                   "7313": {"ags": "7313", "name": "Landau in der Pfalz", "lat": 49.226, "lon": 8.049, "population": 46677, "bundesland": "Rheinland-Pfalz"},
                   "7314": {"ags": "7314", "name": "Ludwigshafen am Rhein", "lat": 49.482, "lon": 8.397, "population": 171061, "bundesland": "Rheinland-Pfalz"},
                   "7315": {"ags": "7315", "name": "Mainz", "lat": 49.974, "lon": 8.241, "population": 217118, "bundesland": "Rheinland-Pfalz"},
                   "7316": {"ags": "7316", "name": "Neustadt an der Weinstraße", "lat": 49.342, "lon": 8.153, "population": 53148, "bundesland": "Rheinland-Pfalz"},
                   "7317": {"ags": "7317", "name": "Pirmasens", "lat": 49.198, "lon": 7.595, "population": 40403, "bundesland": "Rheinland-Pfalz"},
                   "7318": {"ags": "7318", "name": "Speyer", "lat": 49.33, "lon": 8.433, "population": 50378, "bundesland": "Rheinland-Pfalz"},
                   "7319": {"ags": "7319", "name": "Worms", "lat": 49.649, "lon": 8.326, "population": 83330, "bundesland": "Rheinland-Pfalz"},
                   "7320": {"ags": "7320", "name": "Zweibrücken", "lat": 49.248, "lon": 7.364, "population": 34209, "bundesland": "Rheinland-Pfalz"},
                   "7331": {"ags": "7331", "name": "Alzey-Worms", "lat": 49.759, "lon": 8.157, "population": 129244, "bundesland": "Rheinland-Pfalz"},
                   "7332": {"ags": "7332", "name": "Bad Dürkheim", "lat": 49.453, "lon": 8.111, "population": 132660, "bundesland": "Rheinland-Pfalz"},
                   "7333": {"ags": "7333", "name": "Donnersbergkreis", "lat": 49.632, "lon": 7.915, "population": 75101, "bundesland": "Rheinland-Pfalz"},
                   "7334": {"ags": "7334", "name": "Germersheim", "lat": 49.116, "lon": 8.247, "population": 129075, "bundesland": "Rheinland-Pfalz"},
                   "7335": {"ags": "7335", "name": "Kaiserslautern (Landkreis)", "lat": 49.446, "lon": 7.686, "population": 106057, "bundesland": "Rheinland-Pfalz"},
                   "7336": {"ags": "7336", "name": "Kusel", "lat": 49.55, "lon": 7.471, "population": 70526, "bundesland": "Rheinland-Pfalz"},
                   "7337": {"ags": "7337", "name": "Südliche Weinstraße", "lat": 49.19, "lon": 8.049, "population": 110356, "bundesland": "Rheinland-Pfalz"},
                   "7338": {"ags": "7338", "name": "Rhein-Pfalz-Kreis", "lat": 49.416, "lon": 8.361, "population": 154201, "bundesland": "Rheinland-Pfalz"},
                   "7339": {"ags": "7339", "name": "Mainz-Bingen", "lat": 49.922, "lon": 8.078, "population": 210889, "bundesland": "Rheinland-Pfalz"},
                   "7340": {"ags": "7340", "name": "Südwestpfalz", "lat": 49.208, "lon": 7.66, "population": 95113, "bundesland": "Rheinland-Pfalz"},
                   "8111": {"ags": "8111", "name": "Stuttgart", "lat": 48.774, "lon": 9.173, "population": 634830, "bundesland": "Baden-Württemberg"},
                   "8115": {"ags": "8115", "name": "Böblingen", "lat": 48.678, "lon": 8.943, "population": 391640, "bundesland": "Baden-Württemberg"},
                   "8116": {"ags": "8116", "name": "Esslingen", "lat": 48.648, "lon": 9.369, "population": 533859, "bundesland": "Baden-Württemberg"},
                   "8117": {"ags": "8117", "name": "Göppingen", "lat": 48.663, "lon": 9.718, "population": 257253, "bundesland": "Baden-Württemberg"},
                   "8118": {"ags": "8118", "name": "Ludwigsburg", "lat": 48.94, "lon": 9.123, "population": 543984, "bundesland": "Baden-Württemberg"},
                   "8119": {"ags": "8119", "name": "Rems-Murr-Kreis", "lat": 48.899, "lon": 9.501, "population": 426158, "bundesland": "Baden-Württemberg"},
                   "8121": {"ags": "8121", "name": "Heilbronn", "lat": 49.153, "lon": 9.181, "population": 125960, "bundesland": "Baden-Württemberg"},
                   "8125": {"ags": "8125", "name": "Heilbronn (Landkreis)", "lat": 49.177, "lon": 9.191, "population": 343068, "bundesland": "Baden-Württemberg"},
                   "8126": {"ags": "8126", "name": "Hohenlohekreis", "lat": 49.272, "lon": 9.615, "population": 112010, "bundesland": "Baden-Württemberg"},
                   "8127": {"ags": "8127", "name": "Schwäbisch Hall", "lat": 49.144, "lon": 9.909, "population": 195861, "bundesland": "Baden-Württemberg"},
                   "8128": {"ags": "8128", "name": "Main-Tauber-Kreis", "lat": 49.56, "lon": 9.726, "population": 132321, "bundesland": "Baden-Württemberg"},
                   "8135": {"ags": "8135", "name": "Heidenheim", "lat": 48.662, "lon": 10.182, "population": 132472, "bundesland": "Baden-Württemberg"},
                   "8136": {"ags": "8136", "name": "Ostalbkreis", "lat": 48.877, "lon": 10.091, "population": 314002, "bundesland": "Baden-Württemberg"},
                   "8211": {"ags": "8211", "name": "Baden-Baden", "lat": 48.749, "lon": 8.233, "population": 55123, "bundesland": "Baden-Württemberg"},
                   "8212": {"ags": "8212", "name": "Karlsruhe", "lat": 49.012, "lon": 8.412, "population": 313092, "bundesland": "Baden-Württemberg"},
                   "8215": {"ags": "8215", "name": "Karlsruhe (Landkreis)", "lat": 49.082, "lon": 8.563, "population": 444232, "bundesland": "Baden-Württemberg"},
                   "8216": {"ags": "8216", "name": "Rastatt", "lat": 48.761, "lon": 8.241, "population": 231018, "bundesland": "Baden-Württemberg"},
                   "8221": {"ags": "8221", "name": "Heidelberg", "lat": 49.406, "lon": 8.695, "population": 160355, "bundesland": "Baden-Württemberg"},
                   "8222": {"ags": "8222", "name": "Mannheim", "lat": 49.499, "lon": 8.501, "population": 309370, "bundesland": "Baden-Württemberg"},
                   "8225": {"ags": "8225", "name": "Neckar-Odenwald-Kreis", "lat": 49.466, "lon": 9.28, "population": 143535, "bundesland": "Baden-Württemberg"},
                   "8226": {"ags": "8226", "name": "Rhein-Neckar-Kreis", "lat": 49.368, "lon": 8.766, "population": 547625, "bundesland": "Baden-Württemberg"},
                   "8231": {"ags": "8231", "name": "Pforzheim", "lat": 48.876, "lon": 8.713, "population": 125542, "bundesland": "Baden-Württemberg"},
                   "8235": {"ags": "8235", "name": "Calw", "lat": 48.679, "lon": 8.636, "population": 158397, "bundesland": "Baden-Württemberg"},
                   "8236": {"ags": "8236", "name": "Enzkreis", "lat": 48.915, "lon": 8.737, "population": 198905, "bundesland": "Baden-Württemberg"},
                   "8237": {"ags": "8237", "name": "Freudenstadt", "lat": 48.474, "lon": 8.466, "population": 117935, "bundesland": "Baden-Württemberg"},
                   "8311": {"ags": "8311", "name": "Freiburg im Breisgau", "lat": 47.992, "lon": 7.819, "population": 230241, "bundesland": "Baden-Württemberg"},
                   "8315": {"ags": "8315", "name": "Breisgau-Hochschwarzwald", "lat": 47.925, "lon": 7.924, "population": 262795, "bundesland": "Baden-Württemberg"},
                   "8316": {"ags": "8316", "name": "Emmendingen", "lat": 48.149, "lon": 7.897, "population": 165383, "bundesland": "Baden-Württemberg"},
                   "8317": {"ags": "8317", "name": "Ortenaukreis", "lat": 48.421, "lon": 8.016, "population": 429479, "bundesland": "Baden-Württemberg"},
                   "8325": {"ags": "8325", "name": "Rottweil", "lat": 48.254, "lon": 8.533, "population": 139455, "bundesland": "Baden-Württemberg"},
                   "8326": {"ags": "8326", "name": "Schwarzwald-Baar-Kreis", "lat": 48.019, "lon": 8.411, "population": 212381, "bundesland": "Baden-Württemberg"},
                   "8327": {"ags": "8327", "name": "Tuttlingen", "lat": 48.011, "lon": 8.795, "population": 140152, "bundesland": "Baden-Württemberg"},
                   "8335": {"ags": "8335", "name": "Konstanz", "lat": 47.798, "lon": 8.911, "population": 285325, "bundesland": "Baden-Württemberg"},
                   "8336": {"ags": "8336", "name": "Lörrach", "lat": 47.703, "lon": 7.774, "population": 228639, "bundesland": "Baden-Württemberg"},
                   "8337": {"ags": "8337", "name": "Waldshut", "lat": 47.697, "lon": 8.218, "population": 170619, "bundesland": "Baden-Württemberg"},
                   "8415": {"ags": "8415", "name": "Reutlingen", "lat": 48.406, "lon": 9.366, "population": 286748, "bundesland": "Baden-Württemberg"},
                   "8416": {"ags": "8416", "name": "Tübingen", "lat": 48.482, "lon": 8.988, "population": 227331, "bundesland": "Baden-Württemberg"},
                   "8417": {"ags": "8417", "name": "Zollernalbkreis", "lat": 48.267, "lon": 8.937, "population": 188935, "bundesland": "Baden-Württemberg"},
                   "8421": {"ags": "8421", "name": "Ulm", "lat": 48.392, "lon": 9.95, "population": 126329, "bundesland": "Baden-Württemberg"},
                   "8425": {"ags": "8425", "name": "Alb-Donau-Kreis", "lat": 48.402, "lon": 9.828, "population": 196047, "bundesland": "Baden-Württemberg"},
                   "8426": {"ags": "8426", "name": "Biberach", "lat": 48.107, "lon": 9.775, "population": 199742, "bundesland": "Baden-Württemberg"},
                   "8435": {"ags": "8435", "name": "Bodenseekreis", "lat": 47.733, "lon": 9.4, "population": 216227, "bundesland": "Baden-Württemberg"},
                   "8436": {"ags": "8436", "name": "Ravensburg", "lat": 47.825, "lon": 9.781, "population": 284285, "bundesland": "Baden-Württemberg"},
                   "8437": {"ags": "8437", "name": "Sigmaringen", "lat": 48.039, "lon": 9.242, "population": 130873, "bundesland": "Baden-Württemberg"},
                   "9161": {"ags": "9161", "name": "Ingolstadt", "lat": 48.755, "lon": 11.394, "population": 136981, "bundesland": "Bayern"},
                   "9162": {"ags": "9162", "name": "München", "lat": 48.153, "lon": 11.548, "population": 1471508, "bundesland": "Bayern"},
                   "9163": {"ags": "9163", "name": "Rosenheim", "lat": 47.844, "lon": 12.108, "population": 63324, "bundesland": "Bayern"},
                   "9171": {"ags": "9171", "name": "Altötting", "lat": 48.209, "lon": 12.705, "population": 111210, "bundesland": "Bayern"},
                   "9172": {"ags": "9172", "name": "Berchtesgadener Land", "lat": 47.698, "lon": 12.902, "population": 105722, "bundesland": "Bayern"},
                   "9173": {"ags": "9173", "name": "Bad Tölz-Wolfratshausen", "lat": 47.728, "lon": 11.483, "population": 127227, "bundesland": "Bayern"},
                   "9174": {"ags": "9174", "name": "Dachau", "lat": 48.335, "lon": 11.357, "population": 153884, "bundesland": "Bayern"},
                   "9175": {"ags": "9175", "name": "Ebersberg", "lat": 48.076, "lon": 11.912, "population": 142142, "bundesland": "Bayern"},
                   "9176": {"ags": "9176", "name": "Eichstätt", "lat": 48.898, "lon": 11.369, "population": 132341, "bundesland": "Bayern"},
                   "9177": {"ags": "9177", "name": "Erding", "lat": 48.301, "lon": 12.001, "population": 137660, "bundesland": "Bayern"},
                   "9178": {"ags": "9178", "name": "Freising", "lat": 48.447, "lon": 11.74, "population": 179116, "bundesland": "Bayern"},
                   "9179": {"ags": "9179", "name": "Fürstenfeldbruck", "lat": 48.188, "lon": 11.202, "population": 219320, "bundesland": "Bayern"},
                   "9180": {"ags": "9180", "name": "Garmisch-Partenkirchen", "lat": 47.556, "lon": 11.129, "population": 88467, "bundesland": "Bayern"},
                   "9181": {"ags": "9181", "name": "Landsberg am Lech", "lat": 48.025, "lon": 10.949, "population": 120071, "bundesland": "Bayern"},
                   "9182": {"ags": "9182", "name": "Miesbach", "lat": 47.742, "lon": 11.809, "population": 99726, "bundesland": "Bayern"},
                   "9183": {"ags": "9183", "name": "Mühldorf a. Inn", "lat": 48.238, "lon": 12.381, "population": 115250, "bundesland": "Bayern"},
                   "9184": {"ags": "9184", "name": "München (Landkreis)", "lat": 48.075, "lon": 11.631, "population": 348871, "bundesland": "Bayern"},
                   "9185": {"ags": "9185", "name": "Neuburg-Schrobenhausen", "lat": 48.664, "lon": 11.197, "population": 96680, "bundesland": "Bayern"},
                   "9186": {"ags": "9186", "name": "Pfaffenhofen a.d. Ilm", "lat": 48.596, "lon": 11.523, "population": 127151, "bundesland": "Bayern"},
                   "9187": {"ags": "9187", "name": "Rosenheim (Landkreis)", "lat": 47.878, "lon": 12.163, "population": 260983, "bundesland": "Bayern"},
                   "9188": {"ags": "9188", "name": "Starnberg", "lat": 48.006, "lon": 11.282, "population": 136092, "bundesland": "Bayern"},
                   "9189": {"ags": "9189", "name": "Traunstein", "lat": 47.894, "lon": 12.58, "population": 177089, "bundesland": "Bayern"},
                   "9190": {"ags": "9190", "name": "Weilheim-Schongau", "lat": 47.788, "lon": 11.048, "population": 135348, "bundesland": "Bayern"},
                   "9261": {"ags": "9261", "name": "Landshut", "lat": 48.544, "lon": 12.156, "population": 72404, "bundesland": "Bayern"},
                   "9262": {"ags": "9262", "name": "Passau", "lat": 48.582, "lon": 13.417, "population": 52469, "bundesland": "Bayern"},
                   "9263": {"ags": "9263", "name": "Straubing", "lat": 48.881, "lon": 12.572, "population": 47794, "bundesland": "Bayern"},
                   "9271": {"ags": "9271", "name": "Deggendorf", "lat": 48.779, "lon": 13, "population": 119326, "bundesland": "Bayern"},
                   "9272": {"ags": "9272", "name": "Freyung-Grafenau", "lat": 48.827, "lon": 13.513, "population": 78355, "bundesland": "Bayern"},
                   "9273": {"ags": "9273", "name": "Kelheim", "lat": 48.825, "lon": 11.857, "population": 122258, "bundesland": "Bayern"},
                   "9274": {"ags": "9274", "name": "Landshut (Landkreis)", "lat": 48.557, "lon": 12.196, "population": 158698, "bundesland": "Bayern"},
                   "9275": {"ags": "9275", "name": "Passau (Landkreis)", "lat": 48.559, "lon": 13.366, "population": 192043, "bundesland": "Bayern"},
                   "9276": {"ags": "9276", "name": "Regen", "lat": 49.023, "lon": 13.101, "population": 77656, "bundesland": "Bayern"},
                   "9277": {"ags": "9277", "name": "Rottal-Inn", "lat": 48.424, "lon": 12.867, "population": 120659, "bundesland": "Bayern"},
                   "9278": {"ags": "9278", "name": "Straubing-Bogen", "lat": 48.9, "lon": 12.582, "population": 100649, "bundesland": "Bayern"},
                   "9279": {"ags": "9279", "name": "Dingolfing-Landau", "lat": 48.641, "lon": 12.61, "population": 96217, "bundesland": "Bayern"},
                   "9361": {"ags": "9361", "name": "Amberg", "lat": 49.45, "lon": 11.845, "population": 41970, "bundesland": "Bayern"},
                   "9362": {"ags": "9362", "name": "Regensburg", "lat": 49.013, "lon": 12.113, "population": 152610, "bundesland": "Bayern"},
                   "9363": {"ags": "9363", "name": "Weiden i.d. OPf.", "lat": 49.669, "lon": 12.156, "population": 42520, "bundesland": "Bayern"},
                   "9371": {"ags": "9371", "name": "Amberg-Sulzbach", "lat": 49.486, "lon": 11.802, "population": 103109, "bundesland": "Bayern"},
                   "9372": {"ags": "9372", "name": "Cham", "lat": 49.237, "lon": 12.694, "population": 127882, "bundesland": "Bayern"},
                   "9373": {"ags": "9373", "name": "Neumarkt i.d. OPf.", "lat": 49.216, "lon": 11.568, "population": 133561, "bundesland": "Bayern"},
                   "9374": {"ags": "9374", "name": "Neustadt a.d. Waldnaab", "lat": 49.687, "lon": 12.097, "population": 94352, "bundesland": "Bayern"},
                   "9375": {"ags": "9375", "name": "Regensburg (Landkreis)", "lat": 49.022, "lon": 12.121, "population": 193572, "bundesland": "Bayern"},
                   "9376": {"ags": "9376", "name": "Schwandorf", "lat": 49.369, "lon": 12.253, "population": 147189, "bundesland": "Bayern"},
                   "9377": {"ags": "9377", "name": "Tirschenreuth", "lat": 49.899, "lon": 12.201, "population": 72504, "bundesland": "Bayern"},
                   "9461": {"ags": "9461", "name": "Bamberg", "lat": 49.887, "lon": 10.899, "population": 77592, "bundesland": "Bayern"},
                   "9462": {"ags": "9462", "name": "Bayreuth", "lat": 49.938, "lon": 11.587, "population": 74657, "bundesland": "Bayern"},
                   "9463": {"ags": "9463", "name": "Coburg", "lat": 50.265, "lon": 10.965, "population": 41249, "bundesland": "Bayern"},
                   "9464": {"ags": "9464", "name": "Hof", "lat": 50.31, "lon": 11.898, "population": 45930, "bundesland": "Bayern"},
                   "9471": {"ags": "9471", "name": "Bamberg (Landkreis)", "lat": 49.893, "lon": 10.884, "population": 147086, "bundesland": "Bayern"},
                   "9472": {"ags": "9472", "name": "Bayreuth (Landkreis)", "lat": 49.883, "lon": 11.555, "population": 103656, "bundesland": "Bayern"},
                   "9473": {"ags": "9473", "name": "Coburg (Landkreis)", "lat": 50.268, "lon": 10.944, "population": 86906, "bundesland": "Bayern"},
                   "9474": {"ags": "9474", "name": "Forchheim", "lat": 49.721, "lon": 11.173, "population": 116099, "bundesland": "Bayern"},
                   "9475": {"ags": "9475", "name": "Hof (Landkreis)", "lat": 50.273, "lon": 11.819, "population": 95311, "bundesland": "Bayern"},
                   "9476": {"ags": "9476", "name": "Kronach", "lat": 50.329, "lon": 11.373, "population": 67135, "bundesland": "Bayern"},
                   "9477": {"ags": "9477", "name": "Kulmbach", "lat": 50.102, "lon": 11.482, "population": 71845, "bundesland": "Bayern"},
                   "9478": {"ags": "9478", "name": "Lichtenfels", "lat": 50.109, "lon": 11.118, "population": 66838, "bundesland": "Bayern"},
                   "9479": {"ags": "9479", "name": "Wunsiedel i. Fichtelgebirge", "lat": 50.09, "lon": 12.041, "population": 73178, "bundesland": "Bayern"},
                   "9561": {"ags": "9561", "name": "Ansbach", "lat": 49.292, "lon": 10.562, "population": 41847, "bundesland": "Bayern"},
                   "9562": {"ags": "9562", "name": "Erlangen", "lat": 49.581, "lon": 10.978, "population": 111962, "bundesland": "Bayern"},
                   "9563": {"ags": "9563", "name": "Fürth", "lat": 49.491, "lon": 10.965, "population": 127748, "bundesland": "Bayern"},
                   "9564": {"ags": "9564", "name": "Nürnberg", "lat": 49.436, "lon": 11.082, "population": 518365, "bundesland": "Bayern"},
                   "9565": {"ags": "9565", "name": "Schwabach", "lat": 49.336, "lon": 11.022, "population": 40792, "bundesland": "Bayern"},
                   "9571": {"ags": "9571", "name": "Ansbach (Landkreis)", "lat": 49.249, "lon": 10.469, "population": 183949, "bundesland": "Bayern"},
                   "9572": {"ags": "9572", "name": "Erlangen-Höchstadt", "lat": 49.64, "lon": 10.915, "population": 136271, "bundesland": "Bayern"},
                   "9573": {"ags": "9573", "name": "Fürth (Landkreis)", "lat": 49.446, "lon": 10.85, "population": 117387, "bundesland": "Bayern"},
                   "9574": {"ags": "9574", "name": "Nürnberger Land", "lat": 49.491, "lon": 11.37, "population": 170365, "bundesland": "Bayern"},
                   "9575": {"ags": "9575", "name": "Neustadt a.d. Aisch-Bad Windsheim", "lat": 49.569, "lon": 10.465, "population": 100364, "bundesland": "Bayern"},
                   "9576": {"ags": "9576", "name": "Roth", "lat": 49.203, "lon": 11.123, "population": 126958, "bundesland": "Bayern"},
                   "9577": {"ags": "9577", "name": "Weißenburg-Gunzenhausen", "lat": 49.033, "lon": 10.893, "population": 94393, "bundesland": "Bayern"},
                   "9661": {"ags": "9661", "name": "Aschaffenburg", "lat": 49.963, "lon": 9.147, "population": 70527, "bundesland": "Bayern"},
                   "9662": {"ags": "9662", "name": "Schweinfurt", "lat": 50.046, "lon": 10.22, "population": 54032, "bundesland": "Bayern"},
                   "9663": {"ags": "9663", "name": "Würzburg", "lat": 49.785, "lon": 9.942, "population": 127880, "bundesland": "Bayern"},
                   "9671": {"ags": "9671", "name": "Aschaffenburg (Landkreis)", "lat": 50.008, "lon": 9.238, "population": 174208, "bundesland": "Bayern"},
                   "9672": {"ags": "9672", "name": "Bad Kissingen", "lat": 50.223, "lon": 9.965, "population": 103218, "bundesland": "Bayern"},
                   "9673": {"ags": "9673", "name": "Rhön-Grabfeld", "lat": 50.371, "lon": 10.255, "population": 79690, "bundesland": "Bayern"},
                   "9674": {"ags": "9674", "name": "Haßberge", "lat": 50.063, "lon": 10.607, "population": 84599, "bundesland": "Bayern"},
                   "9675": {"ags": "9675", "name": "Kitzingen", "lat": 49.753, "lon": 10.255, "population": 90909, "bundesland": "Bayern"},
                   "9676": {"ags": "9676", "name": "Miltenberg", "lat": 49.758, "lon": 9.235, "population": 128756, "bundesland": "Bayern"},
                   "9677": {"ags": "9677", "name": "Main-Spessart", "lat": 49.993, "lon": 9.663, "population": 126365, "bundesland": "Bayern"},
                   "9678": {"ags": "9678", "name": "Schweinfurt (Landkreis)", "lat": 50.017, "lon": 10.26, "population": 115106, "bundesland": "Bayern"},
                   "9679": {"ags": "9679", "name": "Würzburg (Landkreis)", "lat": 49.738, "lon": 9.927, "population": 161834, "bundesland": "Bayern"},
                   "9761": {"ags": "9761", "name": "Augsburg", "lat": 48.346, "lon": 10.886, "population": 295135, "bundesland": "Bayern"},
                   "9762": {"ags": "9762", "name": "Kaufbeuren", "lat": 47.88, "lon": 10.618, "population": 43893, "bundesland": "Bayern"},
                   "9763": {"ags": "9763", "name": "Kempten (Allgäu)", "lat": 47.738, "lon": 10.309, "population": 68907, "bundesland": "Bayern"},
                   "9764": {"ags": "9764", "name": "Memmingen", "lat": 47.978, "lon": 10.163, "population": 43837, "bundesland": "Bayern"},
                   "9771": {"ags": "9771", "name": "Aichach-Friedberg", "lat": 48.427, "lon": 11.053, "population": 133596, "bundesland": "Bayern"},
                   "9772": {"ags": "9772", "name": "Augsburg (Landkreis)", "lat": 48.355, "lon": 10.732, "population": 251534, "bundesland": "Bayern"},
                   "9773": {"ags": "9773", "name": "Dillingen a.d. Donau", "lat": 48.596, "lon": 10.527, "population": 96021, "bundesland": "Bayern"},
                   "9774": {"ags": "9774", "name": "Günzburg", "lat": 48.353, "lon": 10.38, "population": 125747, "bundesland": "Bayern"},
                   "9775": {"ags": "9775", "name": "Neu-Ulm", "lat": 48.298, "lon": 10.14, "population": 174200, "bundesland": "Bayern"},
                   "9776": {"ags": "9776", "name": "Lindau (Bodensee)", "lat": 47.605, "lon": 9.884, "population": 81669, "bundesland": "Bayern"},
                   "9777": {"ags": "9777", "name": "Ostallgäu", "lat": 47.77, "lon": 10.64, "population": 140316, "bundesland": "Bayern"},
                   "9778": {"ags": "9778", "name": "Unterallgäu", "lat": 48.04, "lon": 10.39, "population": 144041, "bundesland": "Bayern"},
                   "9779": {"ags": "9779", "name": "Donau-Ries", "lat": 48.807, "lon": 10.712, "population": 133496, "bundesland": "Bayern"},
                   "9780": {"ags": "9780", "name": "Oberallgäu", "lat": 47.573, "lon": 10.259, "population": 155362, "bundesland": "Bayern"},
                   "10041": {"ags": "10041", "name": "Regionalverband Saarbrücken", "lat": 49.252, "lon": 6.958, "population": 329708, "bundesland": "Saarland"},
                   "10042": {"ags": "10042", "name": "Merzig-Wadern", "lat": 49.496, "lon": 6.68, "population": 103366, "bundesland": "Saarland"},
                   "10043": {"ags": "10043", "name": "Neunkirchen", "lat": 49.376, "lon": 7.117, "population": 132206, "bundesland": "Saarland"},
                   "10044": {"ags": "10044", "name": "Saarlouis", "lat": 49.355, "lon": 6.776, "population": 195201, "bundesland": "Saarland"},
                   "10045": {"ags": "10045", "name": "Saarpfalz-Kreis", "lat": 49.249, "lon": 7.242, "population": 142631, "bundesland": "Saarland"},
                   "10046": {"ags": "10046", "name": "St. Wendel", "lat": 49.519, "lon": 7.1, "population": 87397, "bundesland": "Saarland"},
                   "11000": {"ags": "11000", "name": "Berlin", "lat": 52.501, "lon": 13.402, "population": 3644826, "bundesland": "Berlin"},
                   "12051": {"ags": "12051", "name": "Brandenburg an der Havel", "lat": 52.4, "lon": 12.515, "population": 72124, "bundesland": "Brandenburg"},
                   "12052": {"ags": "12052", "name": "Cottbus", "lat": 51.773, "lon": 14.366, "population": 100219, "bundesland": "Brandenburg"},
                   "12053": {"ags": "12053", "name": "Frankfurt (Oder)", "lat": 52.325, "lon": 14.49, "population": 57873, "bundesland": "Brandenburg"},
                   "12054": {"ags": "12054", "name": "Potsdam", "lat": 52.425, "lon": 13.029, "population": 178089, "bundesland": "Brandenburg"},
                   "12060": {"ags": "12060", "name": "Barnim", "lat": 52.823, "lon": 13.704, "population": 182760, "bundesland": "Brandenburg"},
                   "12061": {"ags": "12061", "name": "Dahme-Spreewald", "lat": 52.042, "lon": 13.82, "population": 169067, "bundesland": "Brandenburg"},
                   "12062": {"ags": "12062", "name": "Elbe-Elster", "lat": 51.612, "lon": 13.46, "population": 102638, "bundesland": "Brandenburg"},
                   "12063": {"ags": "12063", "name": "Havelland", "lat": 52.621, "lon": 12.629, "population": 161909, "bundesland": "Brandenburg"},
                   "12064": {"ags": "12064", "name": "Märkisch-Oderland", "lat": 52.607, "lon": 14.147, "population": 194328, "bundesland": "Brandenburg"},
                   "12065": {"ags": "12065", "name": "Oberhavel", "lat": 52.907, "lon": 13.206, "population": 211249, "bundesland": "Brandenburg"},
                   "12066": {"ags": "12066", "name": "Oberspreewald-Lausitz", "lat": 51.616, "lon": 13.944, "population": 110476, "bundesland": "Brandenburg"},
                   "12067": {"ags": "12067", "name": "Oder-Spree", "lat": 52.244, "lon": 14.219, "population": 178658, "bundesland": "Brandenburg"},
                   "12068": {"ags": "12068", "name": "Ostprignitz-Ruppin", "lat": 52.992, "lon": 12.636, "population": 99078, "bundesland": "Brandenburg"},
                   "12069": {"ags": "12069", "name": "Potsdam-Mittelmark", "lat": 52.247, "lon": 12.688, "population": 214664, "bundesland": "Brandenburg"},
                   "12070": {"ags": "12070", "name": "Prignitz", "lat": 53.109, "lon": 11.962, "population": 76508, "bundesland": "Brandenburg"},
                   "12071": {"ags": "12071", "name": "Spree-Neiße", "lat": 51.759, "lon": 14.434, "population": 114429, "bundesland": "Brandenburg"},
                   "12072": {"ags": "12072", "name": "Teltow-Fläming", "lat": 52.073, "lon": 13.276, "population": 168296, "bundesland": "Brandenburg"},
                   "12073": {"ags": "12073", "name": "Uckermark", "lat": 53.206, "lon": 13.861, "population": 119552, "bundesland": "Brandenburg"},
                   "13003": {"ags": "13003", "name": "Rostock", "lat": 54.147, "lon": 12.142, "population": 208886, "bundesland": "Mecklenburg-Vorpommern"},
                   "13004": {"ags": "13004", "name": "Schwerin", "lat": 53.623, "lon": 11.416, "population": 95818, "bundesland": "Mecklenburg-Vorpommern"},
                   "13071": {"ags": "13071", "name": "Mecklenburgische Seenplatte", "lat": 53.544, "lon": 13.002, "population": 259130, "bundesland": "Mecklenburg-Vorpommern"},
                   "13072": {"ags": "13072", "name": "Rostock (Landkreis)", "lat": 53.912, "lon": 12.222, "population": 215113, "bundesland": "Mecklenburg-Vorpommern"},
                   "13073": {"ags": "13073", "name": "Vorpommern-Rügen", "lat": 54.283, "lon": 12.992, "population": 224684, "bundesland": "Mecklenburg-Vorpommern"},
                   "13074": {"ags": "13074", "name": "Nordwestmecklenburg", "lat": 53.822, "lon": 11.253, "population": 156729, "bundesland": "Mecklenburg-Vorpommern"},
                   "13075": {"ags": "13075", "name": "Vorpommern-Greifswald", "lat": 53.789, "lon": 13.78, "population": 236697, "bundesland": "Mecklenburg-Vorpommern"},
                   "13076": {"ags": "13076", "name": "Ludwigslust-Parchim", "lat": 53.45, "lon": 11.534, "population": 212618, "bundesland": "Mecklenburg-Vorpommern"},
                   "14511": {"ags": "14511", "name": "Chemnitz", "lat": 50.827, "lon": 12.914, "population": 247237, "bundesland": "Sachsen"},
                   "14521": {"ags": "14521", "name": "Erzgebirgskreis", "lat": 50.609, "lon": 12.946, "population": 337696, "bundesland": "Sachsen"},
                   "14522": {"ags": "14522", "name": "Mittelsachsen", "lat": 50.956, "lon": 13.138, "population": 306185, "bundesland": "Sachsen"},
                   "14523": {"ags": "14523", "name": "Vogtlandkreis", "lat": 50.457, "lon": 12.235, "population": 227796, "bundesland": "Sachsen"},
                   "14524": {"ags": "14524", "name": "Zwickau", "lat": 50.751, "lon": 12.527, "population": 317531, "bundesland": "Sachsen"},
                   "14612": {"ags": "14612", "name": "Dresden", "lat": 51.067, "lon": 13.783, "population": 554649, "bundesland": "Sachsen"},
                   "14625": {"ags": "14625", "name": "Bautzen", "lat": 51.269, "lon": 14.231, "population": 300880, "bundesland": "Sachsen"},
                   "14626": {"ags": "14626", "name": "Görlitz", "lat": 51.225, "lon": 14.751, "population": 254894, "bundesland": "Sachsen"},
                   "14627": {"ags": "14627", "name": "Meißen", "lat": 51.239, "lon": 13.483, "population": 242165, "bundesland": "Sachsen"},
                   "14628": {"ags": "14628", "name": "Sächsische Schweiz-Osterzgebirge", "lat": 50.916, "lon": 13.874, "population": 245611, "bundesland": "Sachsen"},
                   "14713": {"ags": "14713", "name": "Leipzig", "lat": 51.342, "lon": 12.375, "population": 587857, "bundesland": "Sachsen"},
                   "14729": {"ags": "14729", "name": "Leipzig (Landkreis)", "lat": 51.222, "lon": 12.6, "population": 257763, "bundesland": "Sachsen"},
                   "14730": {"ags": "14730", "name": "Nordsachsen", "lat": 51.473, "lon": 12.78, "population": 197673, "bundesland": "Sachsen"},
                   "15001": {"ags": "15001", "name": "Dessau-Roßlau", "lat": 51.853, "lon": 12.231, "population": 81237, "bundesland": "Sachsen-Anhalt"},
                   "15002": {"ags": "15002", "name": "Halle (Saale)", "lat": 51.48, "lon": 11.967, "population": 239257, "bundesland": "Sachsen-Anhalt"},
                   "15003": {"ags": "15003", "name": "Magdeburg", "lat": 52.117, "lon": 11.641, "population": 238697, "bundesland": "Sachsen-Anhalt"},
                   "15081": {"ags": "15081", "name": "Altmarkkreis Salzwedel", "lat": 52.68, "lon": 11.227, "population": 83765, "bundesland": "Sachsen-Anhalt"},
                   "15082": {"ags": "15082", "name": "Anhalt-Bitterfeld", "lat": 51.795, "lon": 12.143, "population": 159854, "bundesland": "Sachsen-Anhalt"},
                   "15083": {"ags": "15083", "name": "Börde", "lat": 52.221, "lon": 11.348, "population": 171734, "bundesland": "Sachsen-Anhalt"},
                   "15084": {"ags": "15084", "name": "Burgenlandkreis", "lat": 51.147, "lon": 11.884, "population": 180190, "bundesland": "Sachsen-Anhalt"},
                   "15085": {"ags": "15085", "name": "Harz", "lat": 51.821, "lon": 10.959, "population": 214446, "bundesland": "Sachsen-Anhalt"},
                   "15086": {"ags": "15086", "name": "Jerichower Land", "lat": 52.261, "lon": 12.027, "population": 89928, "bundesland": "Sachsen-Anhalt"},
                   "15087": {"ags": "15087", "name": "Mansfeld-Südharz", "lat": 51.536, "lon": 11.356, "population": 136249, "bundesland": "Sachsen-Anhalt"},
                   "15088": {"ags": "15088", "name": "Saalekreis", "lat": 51.426, "lon": 11.866, "population": 184582, "bundesland": "Sachsen-Anhalt"},
                   "15089": {"ags": "15089", "name": "Salzlandkreis", "lat": 51.852, "lon": 11.642, "population": 190560, "bundesland": "Sachsen-Anhalt"},
                   "15090": {"ags": "15090", "name": "Stendal", "lat": 52.697, "lon": 11.84, "population": 111982, "bundesland": "Sachsen-Anhalt"},
                   "15091": {"ags": "15091", "name": "Wittenberg", "lat": 51.82, "lon": 12.702, "population": 125840, "bundesland": "Sachsen-Anhalt"},
                   "16051": {"ags": "16051", "name": "Erfurt", "lat": 50.983, "lon": 11.021, "population": 213699, "bundesland": "Thüringen"},
                   "16052": {"ags": "16052", "name": "Gera", "lat": 50.894, "lon": 12.083, "population": 94152, "bundesland": "Thüringen"},
                   "16053": {"ags": "16053", "name": "Jena", "lat": 50.925, "lon": 11.586, "population": 111407, "bundesland": "Thüringen"},
                   "16054": {"ags": "16054", "name": "Suhl", "lat": 50.612, "lon": 10.689, "population": 34835, "bundesland": "Thüringen"},
                   "16055": {"ags": "16055", "name": "Weimar", "lat": 50.978, "lon": 11.317, "population": 65090, "bundesland": "Thüringen"},
                   "16056": {"ags": "16056", "name": "Eisenach", "lat": 50.99, "lon": 10.3, "population": 42370, "bundesland": "Thüringen"},
                   "16061": {"ags": "16061", "name": "Eichsfeld", "lat": 51.384, "lon": 10.254, "population": 100380, "bundesland": "Thüringen"},
                   "16062": {"ags": "16062", "name": "Nordhausen", "lat": 51.503, "lon": 10.731, "population": 83822, "bundesland": "Thüringen"},
                   "16063": {"ags": "16063", "name": "Wartburgkreis", "lat": 50.885, "lon": 10.211, "population": 123025, "bundesland": "Thüringen"},
                   "16064": {"ags": "16064", "name": "Unstrut-Hainich-Kreis", "lat": 51.185, "lon": 10.551, "population": 102912, "bundesland": "Thüringen"},
                   "16065": {"ags": "16065", "name": "Kyffhäuserkreis", "lat": 51.325, "lon": 10.986, "population": 75009,                             "bundesland": "Thüringen"},
                   "16066": {"ags": "16066", "name": "Schmalkalden-Meiningen", "lat": 50.63, "lon": 10.405, "population": 122347,                             "bundesland": "Thüringen"},
                   "16067": {"ags": "16067", "name": "Gotha", "lat": 50.91, "lon": 10.694, "population": 135452, "bundesland": "Thüringen"},
                   "16068": {"ags": "16068", "name": "Sömmerda", "lat": 51.157, "lon": 11.153, "population": 69655, "bundesland": "Thüringen"},
                   "16069": {"ags": "16069", "name": "Hildburghausen", "lat": 50.434, "lon": 10.735, "population": 63553,                             "bundesland": "Thüringen"},
                   "16070": {"ags": "16070", "name": "Ilm-Kreis", "lat": 50.738, "lon": 10.966, "population": 108742, "bundesland": "Thüringen"},
                   "16071": {"ags": "16071", "name": "Weimarer Land", "lat": 50.972, "lon": 11.374, "population": 81947, "bundesland": "Thüringen"},
                   "16072": {"ags": "16072", "name": "Sonneberg", "lat": 50.415, "lon": 11.133, "population": 56196, "bundesland": "Thüringen"},
                   "16073": {"ags": "16073", "name": "Saalfeld-Rudolstadt", "lat": 50.638, "lon": 11.308, "population": 106356,                             "bundesland": "Thüringen"},
                   "16074": {"ags": "16074", "name": "Saale-Holzland-Kreis", "lat": 50.904, "lon": 11.732, "population": 83051,                             "bundesland": "Thüringen"},
                   "16075": {"ags": "16075", "name": "Saale-Orla-Kreis", "lat": 50.581, "lon": 11.71, "population": 80868,                             "bundesland": "Thüringen"},
                   "16076": {"ags": "16076", "name": "Greiz", "lat": 50.749, "lon": 12.073, "population": 98159, "bundesland": "Thüringen"},
                   "16077": {"ags": "16077", "name": "Altenburger Land", "lat": 50.956, "lon": 12.4, "population": 90118,                             "bundesland": "Thüringen"}}

number_by_name = {j['name']: i for i, j in zeit_kreise_key.items()}
name_by_number = {i: j['name'] for i, j in zeit_kreise_key.items()}


def get_data_by_name(name):
    kreise = get_cached(ZEIT_KREISE_URL)
    kreise = kreise.json()['kreise']
    kreise_dict = {j['ags']: j for j in kreise['items']}
    limits = {i: datetime.datetime.strptime(j, "%Y-%m-%d") for i, j in kreise['meta']['historicalStats'].items()}
    x = [limits['start'] + datetime.timedelta(days=n) for n in range(0, (limits['end'] - limits['start']).days + 1)]
    return zeit_kreise_key[number_by_name[name]], x, kreise_dict[number_by_name[name]]


def get_current_data():
    kreise = get_cached(ZEIT_KREISE_URL)
    kreise = kreise.json()['kreise']
    kreise_dict = {name_by_number[j['ags']]: {**j['currentStats'], **zeit_kreise_key[j['ags']],
                                              **{"week_new": (j['currentStats']['count'] -
                                                              j['historicalStats']['count'][-8]) /
                                                             zeit_kreise_key[j['ags']]['population'] * 100000,
                                                 "week_recovered": (j['currentStats']['recovered'] - list(
                                                     propagate_none(j['historicalStats']['recovered']))[-7]) /
                                                                   zeit_kreise_key[j['ags']]['population'] * 100000}}
                   for j in kreise['items']}
    return kreise_dict


def propagate_none(list):
    default = 0
    for i in list:
        if i is None:
            yield default
        else:
            default = i
            yield i


def plot_kreis(name):
    kreis_data, x, kreise_dict = get_data_by_name(name)
    # fig = matplotlib.pyplot.figure(figsize=(5, 5), dpi=300)
    fig = matplotlib.pyplot.figure(dpi=300)
    ax = fig.add_subplot()

    reported = list(propagate_none(kreise_dict['historicalStats']['count']))
    recovered = list(propagate_none(kreise_dict['historicalStats']['recovered']))
    deaths = list(propagate_none(kreise_dict['historicalStats']['dead']))
    longest = max([len(reported), len(recovered), len(deaths)])
    while longest > len(reported):
        reported.append(reported[-1])
    while longest > len(recovered):
        recovered.append(recovered[-1])
    while longest > len(deaths):
        deaths.append(deaths[-1])

    reported = np.array(reported)
    recovered = np.array(recovered)
    deaths = np.array(deaths)

    active = reported - recovered - deaths

    fig, axes = matplotlib.pyplot.subplots(nrows=2, ncols=1, sharex=True, sharey=True, figsize=(5, 5), dpi=300)

    ax, ax1 = axes
    ax3 = ax1.twinx()
    ax2 = ax.twinx()

    # ax.plot(x, deaths, "b.", label="deaths/confirmed cases")
    ax.plot([d + datetime.timedelta(days=7) for d in x], np.array(reported) + (kreis_data['population'] * 50 / 100000),
            color="black", label="lockdown limit")

    ax.bar(x, reported, color="red", label="reported")
    ax.bar(x, recovered, color="green", label="recovered")
    ax.bar(x, deaths, color="black", label="deaths")

    ax.set_xlim((x[30], x[-1] + datetime.timedelta(days=1)))

    ax1.bar(x, active, label="active cases")
    ax1.legend(loc=2)
    ax.legend(loc=2)

    ax.set_ylabel(f"cases")
    ax2.set_ylabel("cases")
    matplotlib.pyplot.setp(ax1.get_xticklabels(), rotation=25, ha="right", rotation_mode="anchor")

    ax2.set_ylim((i * 1.0 / kreis_data['population'] * 100000 for i in ax.get_ylim()))
    ax3.set_ylim((i * 1.0 / kreis_data['population'] * 100000 for i in ax1.get_ylim()))
    ax2.set_ylabel("per 100k")
    ax3.set_ylabel("per 100k")

    bio = BytesIO()
    FigureCanvas(fig)
    fig.tight_layout()
    fig.savefig(bio, format="svg")
    matplotlib.pyplot.close(fig)
    return bio.getvalue()


if __name__ == "__main__":
    a = get_current_data()
    res = get_cached(ZEIT_KREISE_URL).json()
    print(res)

    da = plot_kreis("Heilbronn")
    open("test.svg", "wb").write(da)
    print("yes")
