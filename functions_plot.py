import os
import pandas as pd
import glob
from datetime import date
import numpy as np

from tempfile import NamedTemporaryFile
from PIL import Image
import urllib

from mplsoccer import Bumpy, FontManager, add_image, Pitch, VerticalPitch, PyPizza, Radar, grid
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.ticker as ticker
from matplotlib import rcParams
import matplotlib.patheffects as path_effects
import matplotlib.patches as patches
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
from matplotlib.offsetbox import (OffsetImage, AnnotationBbox)
from matplotlib.patches import FancyBboxPatch

github_url = 'https://github.com/google/fonts/blob/main/ofl/poppins/Poppins-Bold.ttf'
url = github_url + '?raw=true'

response = urllib.request.urlopen(url)
f = NamedTemporaryFile(delete=False, suffix='.ttf')
f.write(response.read())
f.close()

bold = fm.FontProperties(fname=f.name)

github_url = 'https://github.com/google/fonts/blob/main/ofl/poppins/Poppins-Regular.ttf'
url = github_url + '?raw=true'

response = urllib.request.urlopen(url)
f = NamedTemporaryFile(delete=False, suffix='.ttf')
f.write(response.read())
f.close()

reg = fm.FontProperties(fname=f.name)

github_url = 'https://github.com/google/fonts/blob/main/ofl/poppins/Poppins-Italic.ttf'
url = github_url + '?raw=true'

response = urllib.request.urlopen(url)
f = NamedTemporaryFile(delete=False, suffix='.ttf')
f.write(response.read())
f.close()

ita = fm.FontProperties(fname=f.name)

path_eff = [path_effects.Stroke(linewidth=2, foreground='#ffffff'),
            path_effects.Normal()]

def create_chart(teamz, data):
  datas = data.copy()
  teams = datas['Team'].tolist()
  teams = reversed(teams)
  match_day = datas.columns.tolist()[1:]
  season_dict = datas.set_index('Team').T.to_dict('list')
  team_list = teamz
  highlight_dict = {
      "Arema FC": "#0088CC",
      "PERSIB": "#00599C",
      "PSIM Yogyakarta": "#003366",
      "Semen Padang FC": "#D40027",
      "PERSIS": "#A51C30",
      "PSM Makassar": "#E31D1A",
      "PERSIJAP": "#CC0000",
      "Bali United FC": "#E31D24",
      "Madura United FC": "#D9232D",
      "Malut United FC": "#D91E18",
      "PERSIJA": "#E71D3A",
      "Bhayangkara Presisi Lampung FC": "#FFD700",
      "Borneo FC Samarinda": "#8F1C21",
      "Dewa United Banten FC": "#000000",
      "PERSEBAYA Surabaya": "#008B4E",
      "PERSIK Kediri": "#591F79",
      "PERSITA": "#4E2A84",
      "PSBS Biak": "#87CEEB"
  }
  selected_teams = {
      key: highlight_dict[key]
      for key in team_list
      if key in highlight_dict
      }

  bumpy = Bumpy(
      background_color="#FFFFFF", scatter_color="#8FA1D2",
      label_color="#1F4196", line_color="#BACAF7",
      ticklabel_size=17, label_size=30,
      scatter_primary='D',
      show_right=False,
      plot_labels=True,
      alignment_yvalue=0.5,
      alignment_xvalue=0.065
  )

  fig, ax = bumpy.plot(
      x_list=match_day,
      y_list=np.linspace(1, 18, 18).astype(int),
      values=season_dict,
      secondary_alpha=0.5,
      highlight_dict=selected_teams,
      figsize=(34, 18),
      ylim=(-0.1, 20),
      lw=2.5,
      fontproperties=bold,
  )

  DC_to_FC = ax.transData.transform
  FC_to_NFC = fig.transFigure.inverted().transform
  DC_to_NFC = lambda x: FC_to_NFC(DC_to_FC(x))

  for index, team in enumerate(teams):
      ax_coords = DC_to_NFC([13.25, index+0.5])
      logo_ax = fig.add_axes([ax_coords[0], ax_coords[1], 0.035, 0.035], anchor = "C")
      club_icon = Image.open('./logo/'+team+'.png')
      logo_ax.imshow(club_icon)
      logo_ax.axis("off")
  
  fig.savefig('chart.jpg', dpi=500, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
  
  return fig
