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

metrik = ['Name','Team','MoP','Non-penalty goals','Non-penalty xG','NPxG/Shot','Shots','Shot on target ratio','Conversion ratio','Chances created','Assists',
          'Passes-to-box','Through passes','Passes to final 3rd','Progressive passes','Long passes','Pass accuracy','Successful crosses',
          'Successful dribbles','Offensive duel won ratio','Tackles','Intercepts','Recoveries','Blocks','Clearances','Aerial duel won ratio',
          'Defensive duel won ratio','Passes','Passes received','Clean sheets','Shots on target faced','xGOT against','Goals conceded','Goals prevented',
          'Save ratio','Sweepers','Crosses claimed']

jamet = ['Name','Team','MoP','Non-penalty goals','Shots','Chances created','Assists','Through passes','Progressive passes',
         'Long passes','Successful crosses','Successful dribbles','Tackles','Intercepts','Recoveries','Blocks','Clearances',
         'Total Pass','Aerial Duels','Offensive Duel','Offensive Duel - Won','Defensive Duel','Defensive Duel - Won','Goal',
         'Shot on','Pass','Aerial Won','Penalty','Passes','Clean sheets','Sweepers','Crosses claimed']

posdict = {'gk':{'position':'Goalkeeper',
                 'metrics':['Name','Passes','Pass accuracy','Long passes','Progressive passes','Passes received','Clean sheets','Shots on target faced',
                            'xGOT against','Goals conceded','Goals prevented','Save ratio','Sweepers','Crosses claimed','Intercepts']},
           'cb':{'position':'Center Back',
                 'metrics':['Name','Non-penalty goals','Shots',
                            'Passes to final 3rd','Progressive passes','Long passes','Pass accuracy',
                            'Tackles','Intercepts','Recoveries','Blocks','Clearances','Aerial duel won ratio','Defensive duel won ratio']},
           'fb':{'position':'Fullback',
                 'metrics':['Name','Non-penalty goals','Non-penalty xG','Shots','Chances created','Assists',
                            'Passes-to-box','Through passes','Passes to final 3rd','Progressive passes','Pass accuracy','Successful dribbles','Successful crosses','Offensive duel won ratio',
                            'Tackles','Intercepts','Recoveries','Blocks','Clearances','Aerial duel won ratio','Defensive duel won ratio']},
           'cm':{'position':'Midfielder',
                 'metrics':['Name','Non-penalty goals','Non-penalty xG','NPxG/Shot','Shots','Shot on target ratio','Chances created','Assists',
                            'Passes-to-box','Through passes','Passes to final 3rd','Progressive passes','Long passes','Pass accuracy','Successful dribbles','Offensive duel won ratio',
                            'Tackles','Intercepts','Recoveries','Clearances','Defensive duel won ratio']},
           'cam/w':{'position':'Attacking 10/Winger',
                    'metrics':['Name','Non-penalty goals','Non-penalty xG','NPxG/Shot','Shots','Shot on target ratio','Conversion ratio','Chances created','Assists',
                               'Passes-to-box','Through passes','Passes to final 3rd','Progressive passes','Pass accuracy','Successful dribbles','Offensive duel won ratio',
                               'Tackles','Intercepts','Recoveries','Defensive duel won ratio']},
           'fw':{'position':'Forward',
                 'metrics':['Name','Non-penalty goals','Non-penalty xG','NPxG/Shot','Shots','Shot on target ratio','Conversion ratio','Chances created','Assists',
                            'Passes-to-box','Through passes','Progressive passes','Pass accuracy','Successful dribbles','Offensive duel won ratio',
                            'Tackles','Intercepts','Recoveries','Aerial duel won ratio','Defensive duel won ratio']}}

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
  '''
  DC_to_FC = ax.transData.transform
  FC_to_NFC = fig.transFigure.inverted().transform
  DC_to_NFC = lambda x: FC_to_NFC(DC_to_FC(x))

  for index, team in enumerate(teams):
      ax_coords = DC_to_NFC([13.25, index+0.5])
      logo_ax = fig.add_axes([ax_coords[0], ax_coords[1], 0.035, 0.035], anchor = "C")
      club_icon = Image.open('./logo/'+team+'.png')
      logo_ax.imshow(club_icon)
      logo_ax.axis("off")
  '''
  fig.savefig('chart.jpg', dpi=500, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
  
  return fig

def beli_pizza(komp, pos, klub, name, data, mins):
  df = data.copy()
  df = df[df['Position']==pos]

  #DATA
  if (pos=='Forward'):
    temp = df[posdict['fw']['metrics']].reset_index(drop=True)
    temp = temp[(temp['Name']==name) | (temp['Name']=='Average FW')].reset_index(drop=True)

    slice_colors = ['#16317d']*8 + ['#a40000']*6 + ['#ffcd12']*5

  elif (pos=='Winger') or (pos=='Attacking Midfielder'):
    temp = df[posdict['cam/w']['metrics']].reset_index(drop=True)
    if (pos=='Winger'):
      temp = temp[(temp['Name']==name) | (temp['Name']=='Average W')].reset_index(drop=True)
    else:
      temp = temp[(temp['Name']==name) | (temp['Name']=='Average CAM')].reset_index(drop=True)

    slice_colors = ['#16317d']*8 + ['#a40000']*7 + ['#ffcd12']*4

  elif (pos=='Midfielder'):
    temp = df[posdict['cm']['metrics']].reset_index(drop=True)
    temp = temp[(temp['Name']==name) | (temp['Name']=='Average CM')].reset_index(drop=True)

    slice_colors = ['#16317d']*7 + ['#a40000']*8 + ['#ffcd12']*5

  elif (pos=='Side Back'):
    temp = df[posdict['fb']['metrics']].reset_index(drop=True)
    temp = temp[(temp['Name']==name) | (temp['Name']=='Average FB')].reset_index(drop=True)

    slice_colors = ['#16317d']*5 + ['#a40000']*8 + ['#ffcd12']*7

  elif (pos=='Center Back'):
    temp = df[posdict['cb']['metrics']].reset_index(drop=True)
    temp = temp[(temp['Name']==name) | (temp['Name']=='Average CB')].reset_index(drop=True)

    slice_colors = ['#16317d']*2 + ['#a40000']*4 + ['#ffcd12']*7

  elif (pos=='Goalkeeper'):
    temp = df[posdict['gk']['metrics']].reset_index(drop=True)
    temp = temp[(temp['Name']==name) | (temp['Name']=='Average GK')].reset_index(drop=True)

    slice_colors = ['#16317d']*5 + ['#a40000']*6 + ['#ffcd12']*3

  #temp = temp.drop(['Team'], axis=1)

  avg_player = temp[temp['Name'].str.contains('Average')]
  av_name = list(avg_player['Name'])[0]
  params = list(temp.columns)
  params = params[1:]

  a_values = []
  b_values = []

  for x in range(len(temp['Name'])):
    if temp['Name'][x] == name:
      a_values = temp.iloc[x].values.tolist()
    if temp['Name'][x] == av_name:
      b_values = temp.iloc[x].values.tolist()

  a_values = a_values[1:]
  b_values = b_values[1:]

  values = [a_values,b_values]
  maxmin = pd.DataFrame({'param':params,'value':a_values,'average':b_values})
  for index, value in enumerate(params):
    if value == 'Progressive passes':
      params[index] = 'Progressive\npasses'
    elif value == 'long passes':
      params[index] = 'Long\npasses'
    elif value == 'Pass accuracy':
      params[index] = 'Pass\naccuracy'
    elif value == 'Successful crosses':
      params[index] = 'Successful\ncrosses'
    elif value == 'Successful dribbles':
      params[index] = 'Successful\ndribbles'
    elif value == 'Offensive duel won ratio':
      params[index] = 'Offensive duel\nwon ratio'
    elif value == 'Defensive duel won ratio':
      params[index] = 'Defensive duel\nwon ratio'
    elif value == 'Aerial duel won ratio':
      params[index] = 'Aerial\nduel won\nratio'
    elif value == 'Passes to final 3rd':
      params[index] = 'Passes to\nfinal 3rd'
    elif value == 'Through passes':
      params[index] = 'Through\npasses'
    elif value == 'Non-penalty goals':
      params[index] = 'Non-penalty\ngoals'
    elif value == 'Shot on target ratio':
      params[index] = 'Shot on\ntarget ratio'
    elif value == 'Conversion ratio':
      params[index] = 'Conversion\nratio'
    elif value == 'Chances created':
      params[index] = 'Chances\ncreated'
    elif value == 'Shots on target faced':
      params[index] = 'Shots on\ntarget faced'
    elif value == 'Goals prevented':
      params[index] = 'Goals\nprevented'
    elif value == 'Goals conceded':
      params[index] = 'Goals\nconceded'

  #PLOT
  # set figure size
  fig = plt.figure(figsize=(10,10))

  # plot polar axis
  ax = plt.subplot(111, polar=True)
  ax.set_theta_direction(-1)
  ax.set_theta_zero_location('N')

  # Set the grid and spine off
  fig.patch.set_facecolor('#FFFFFF')
  ax.set_facecolor('#FFFFFF')
  ax.spines['polar'].set_visible(False)
  plt.axis('off')

  # Add line in 20, 40, 60, 80
  x2 = np.linspace(0, 2*np.pi, 50)
  annot_x = [20 + x*20 for x in range(0,4)]
  for z in annot_x:
    ax.plot(x2, [z]*50, color='#000000', lw=1, ls='--', alpha=0.15, zorder=4)
  ax.plot(x2, [100]*50, color='#000000', lw=2, zorder=10, alpha=0.5, ls='-')
  # Set the coordinates limits
  upperLimit = 100
  lowerLimit = 0

  # Compute max and min in the dataset
  max = maxmin['value'].max()

  # Let's compute heights: they are a conversion of each item value in those new coordinates
  # In our example, 0 in the dataset will be converted to the lowerLimit (10)
  # The maximum will be converted to the upperLimit (100)
  slope = (max-lowerLimit)/max
  heights = slope*maxmin['value'] + lowerLimit
  avg_heights = slope*maxmin['average'] + lowerLimit
  va_heights = maxmin['value']*0 + 90
  #shadow = df.Value*0 + 100

  # Compute the width of each bar. In total we have 2*Pi = 360°
  width = 2*np.pi/len(a_values)

  # Compute the angle each bar is centered on:
  indexes = list(range(1, len(a_values)+1))
  angles = [element*width for element in indexes]

  # Draw bars
  bars = ax.bar(x=angles, height=heights, width=width, bottom=lowerLimit, linewidth=2, edgecolor='#FFFFFF', zorder=3, alpha=1, color=slice_colors)
  #bars = ax.bar(x=angles, height=shadow, width=width, bottom=lowerLimit, linewidth=2, edgecolor='#000000', zorder=2, alpha=0.15, color=slice_colors)

  # Draw scatter plots for the averages and values
  scas_av = ax.scatter(x=angles, y=avg_heights, s=150, c=slice_colors, zorder=5, ec='#000000')
  #scas_va = ax.scatter(x=angles, y=va_heights, s=350, c='#000000',
  #                     zorder=4, marker='s', lw=0.5, ec='#ffffff')

  # Draw vertical lines for reference
  ax.vlines(angles, 0, 100, color='#000000', ls='--', zorder=4, alpha=0.35)

  # Add labels
  for bar, angle, height, label, value in zip(bars,angles, heights, params, a_values):
    # Labels are rotated. Rotation must be specified in degrees :(
    rotation = np.rad2deg((np.pi/2)-angle)
    # Flip some labels upside down
    if (angle <= np.pi/2) or (angle >= (np.pi/2)+np.pi):
        rotation = rotation+270
    else:
        rotation = rotation+90

    # Finally add the labels and values
    ax.text(x=angle, y=110, s=label, color='#000000', ha='center',
            va='center', rotation=rotation, rotation_mode='anchor',
            fontproperties=reg)
    ax.text(x=angle, y=90, s=value, color='#000000', zorder=11, va='center',
            ha='center', fontproperties=bold, bbox=dict(facecolor='#FFFFFF', edgecolor='#000000',
                                                        boxstyle='circle, pad=0.5'))
  if pos=='Goalkeeper':
    fig.text(0.325, 0.9325, "Distribution                                GK Metric                            Defending",
             fontproperties=reg, size=10, color='#000000', va='center')
  else:
    fig.text(0.325, 0.9325, "Attacking                                Possession                            Defending",
             fontproperties=reg, size=10, color='#000000', va='center')

  fig.patches.extend([plt.Circle((0.305, 0.935), 0.01, fill=True, color='#16317d',
                                    transform=fig.transFigure, figure=fig),
                      plt.Circle((0.490, 0.935), 0.01, fill=True, color='#a40000',
                                    transform=fig.transFigure, figure=fig),
                      plt.Circle((0.668, 0.935), 0.01, fill=True, color='#ffcd12',
                                    transform=fig.transFigure, figure=fig),
                      plt.Circle((0.15, 0.0425), 0.01, fill=True, color='#000000',
                                 transform=fig.transFigure, figure=fig)])

  fig.text(0.515, 0.985,name + ' - ' + klub, fontproperties=bold, size=18,
           ha='center', color='#000000')
  fig.text(0.515, 0.963, 'Percentile Rank vs League Average '+pos,
           fontproperties=reg, size=11, ha='center', color='#000000')

  fig.text(0.17, 0.04, 'League Average', fontproperties=reg, size=10, color='#000000', va='center')

  CREDIT_1 = 'BRI Super League'
  CREDIT_2 = 'Season 2025/26 | Min. '+str(mins)+' mins played'

  fig.text(0.515, 0.025, f'{CREDIT_1}\n{CREDIT_2}', fontproperties=reg,
           size=11, color='#000000', ha='center')
  '''
  DC_to_FC = ax.transData.transform
  FC_to_NFC = fig.transFigure.inverted().transform
  DC_to_NFC = lambda x: FC_to_NFC(DC_to_FC(x))

  logo_ax = fig.add_axes([0.73, 0.015, 0.15, 0.05], anchor = "NE")
  club_icon = Image.open('logo2.png')
  logo_ax.imshow(club_icon)
  logo_ax.axis("off")
  '''
  fig.savefig('pizza.jpg', dpi=500, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')

  return fig
