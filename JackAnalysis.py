import ROOT
import uproot
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import seaborn as sns
from scipy.optimize import curve_fit

### comand lines to run before sims/analysis:
### source /opt/root/bin/thisroot.sh
### export LD_LIBRARY_PATH=/opt/geant4/lib:$LD_LIBRARY_PATH
### export LD_LIBRARY_PATH=/home/s2225314/Documents/Masters-project/MPHYS/initial-proj/vgm_install/lib:$LD_LIBRARY_PATH

geometry = 'krakow'

def readFile(filePath, treeName, desiredBranches = None, sorted = False):
   file = ROOT.TFile.Open(filePath)
   print(file.ls())
   tree = file.Get(treeName)

   # Convert TTree to Pandas DataFrame
   #npArray = tree.arrays(desiredBranches, library='np')
   #import ROOT

   #f = ROOT.TFile.Open(filePath)
   #tree = f.Get("trackingData;19")

   #tree.Print()

   #for branch in tree.GetListOfBranches():
   #   print(branch.GetName())

   centroidRows = []
   trackRows = []
   if sorted:
      for event_idx, event in enumerate(tree):
         for centroid_idx, centroid in enumerate(event.centroids):
            centroidRows.append({
                  "event": event_idx,
                  "centroid": centroid_idx,
                  "x": centroid.x,
                  "y": centroid.y,
                  "z": centroid.z,
                  "sigmaX": centroid.sigma_x,
                  "sigmaY": centroid.sigma_y,
                  "sigmaZ": centroid.sigma_z,
            })
         for trackIdx, track in enumerate(event.tracks):
            trackRows.append({
                  "event": event_idx,
                  "track": trackIdx,
                  "points": track.nPoints,
                  "slopeXY": track.slope_xy,
                  "slopeZY": track.slope_zy,
                  "interceptXY": track.intercept_xy,
                  "interceptZY": track.intercept_zy,
                  "X" : list(track.x),
                  "Y" : list(track.y),
                  "Z" : list(track.z),
                  "sigmaX" : list(track.sigmas_x),
                  "sigmaY" : list(track.sigmas_y),
                  "sigmaZ" : list(track.sigmas_z),
                  "Chi2XY" : track.chi2_xy,
                  "Chi2ZY" : track.chi2_zy,
                  "slopeXYErr" : track.slope_xy_err,
                  "slopeZYErr" : track.slope_zy_err,
                  "interceptXYErr" : track.intercept_xy_err,
                  "interceptZYErr" : track.intercept_zy_err,                                    
            })

   centroidsDF = pd.DataFrame(centroidRows)
   tracksDF = pd.DataFrame(trackRows)

   df = ROOT.RDataFrame(tree).AsNumpy(desiredBranches)
   df = pd.DataFrame(df)
   #print(f'Length of array {len(df)}, Df type: {type(df)}')
   return df, centroidsDF, tracksDF

def TrackSlopeDistriution(dataTracks):
   print(f'{'='*80}\nPlotting Track and Slope Distributions Start\n{'='*80}')

   legend_elements = [Line2D([0], [0], marker='o', label='No track',
                          markerfacecolor='r', color='w'),
                     Line2D([0], [0], marker='o', label='Track',
                          markerfacecolor='blue', color='w'),]
   dataTracks['colour'] = np.where(dataTracks["points"] > 7, "b", "r")
   xlabels = ['slopeXY', 'slopeXY', 'interceptXY']#, 'angleXY']
   ylabels = ['slopeZY', 'interceptXY', 'interceptZY']#, 'angleZY']
   titles = ['slopeXY_vs_slopeZY', 'slopeXY_vs_interceptXY', 'interceptXY_vs_interceptZY']#, 'angleXY_vs_angleZY']
   ylims = [(-1,1),(-125, 125),(-125, 125)]
   xlims = [(-1,1),(-1, 1),(-125, 125)]
   for i in range(len(xlabels)):
      plt.figure()
      plt.scatter(dataTracks[xlabels[i]], dataTracks[ylabels[i]], color = dataTracks['colour'], edgecolors='k')
      plt.legend(handles=legend_elements)
      plt.xlabel(xlabels[i])
      plt.ylabel(ylabels[i])
      plt.ylim(ylims[i])
      plt.xlim(xlims[i])
      plt.title(titles[i])
      #plt.show()
      plt.savefig(f'JackData/{titles[i]}_{geometry}.png')
   trueTracks = dataTracks[dataTracks['colour'] == 'b']
   for i in range(len(xlabels)):
      plt.figure()
      plt.scatter(trueTracks[xlabels[i]], trueTracks[ylabels[i]], color = 'b', edgecolors='k')
      plt.legend(handles=legend_elements)
      plt.xlabel(xlabels[i])
      plt.ylabel(ylabels[i])
      plt.ylim(ylims[i])
      plt.xlim(xlims[i])
      plt.title(f'{titles[i]} (Tracks only)')
      #plt.show()
      plt.savefig(f'JackData/{titles[i]}_{geometry}_tracks.png')
   print(f'{'='*80}\nPlotting Track and Slope Distributions End\n{'='*80}')

#def PredictPositions(dataFrame):

def CalculateResiduals(dataTracks):

   dataTracks['predictedX'] = [
    intercept + slope * np.asarray(y)
    for intercept, slope, y in zip(
        dataTracks['interceptXY'],
        dataTracks['slopeXY'],
        dataTracks['Y']
    )
]
   dataTracks['predictedZ'] = [
    intercept + slope * np.asarray(y)
    for intercept, slope, y in zip(
        dataTracks['interceptZY'],
        dataTracks['slopeZY'],
        dataTracks['Y']
    )
]
   digitizationResidualsX = [trueX - predictedX for trueX,predictedX in zip(dataTracks['X'], dataTracks['predictedX'])]
   digitizationResidualsZ = [trueZ - predictedZ for trueZ,predictedZ in zip(dataTracks['Z'], dataTracks['predictedZ'])]

   return digitizationResidualsX, digitizationResidualsZ

def AverageResiduals(dataTracks, cut = None):
   digitizationResidualsX, digitizationResidualsZ = CalculateResiduals(dataTracks)
   AverageXResiduals = np.zeros(len(digitizationResidualsX))
   AverageZResiduals = np.zeros(len(digitizationResidualsZ))
   for i in range(len(digitizationResidualsX)):
      AverageXResiduals[i] = np.mean(digitizationResidualsX[i])
      AverageZResiduals[i] = np.mean(digitizationResidualsZ[i])
   return AverageXResiduals, AverageZResiduals

def AverageAbsoluteResiduals(dataTracks):
   digitizationResidualsX, digitizationResidualsZ = CalculateResiduals(dataTracks)
   AverageAsoluteXResiduals = np.zeros(len(digitizationResidualsX))
   AverageAsoluteZResiduals = np.zeros(len(digitizationResidualsZ))
   for i in range(len(digitizationResidualsX)):
      AverageAsoluteXResiduals[i] = np.mean(np.abs(digitizationResidualsX[i]))
      AverageAsoluteZResiduals[i] = np.mean(np.abs(digitizationResidualsZ[i]))
   return AverageAsoluteXResiduals, AverageAsoluteZResiduals

def AverageResidualsSegentation(dataTracks):
   AverageX, AverageZ = AverageResiduals(dataTracks)
   return np.mean(AverageX), np.mean(AverageZ)

def AverageCutResiduals(dataFrame, cuts):
   xResidualsCut = AddCutColumn(dataFrame, 'XResiduals', cuts[0], cuts[1])
   zResidualsCut = AddCutColumn(dataFrame, 'ZResiduals', cuts[2], cuts[3])     

   AverageCutXResiduals = np.zeros(xResidualsCut.shape[0])
   AverageCutZResiduals = np.zeros(zResidualsCut.shape[0])
   for i in range(len(AverageCutXResiduals)):
      AverageCutXResiduals[i] = np.mean(xResidualsCut[i])
      AverageCutZResiduals[i] = np.mean(zResidualsCut[i])

   return AverageCutXResiduals, AverageCutZResiduals

def AverageCutResidualsSegmentation(dataFrame, cuts):
   averageX, averageZ = AverageCutResiduals(dataFrame, cuts)
   #print(f'In Average Segmentation, array lengths: X : {np.shape(averageX)}, Z : {len(averageZ)}')
   #print(f'Average Values : X = {np.mean(averageX)}, Z = {np.mean(averageZ)}, First 5 X values: {averageX[:5]}, nans.. {np.argwhere(averageX == np.nan)} ')
   return np.mean(averageX[np.invert(np.isnan(averageX))]), np.mean(averageZ[np.invert(np.isnan(averageZ))])

def AverageCutAbsoluteResidualsSegmentation(dataFrame, cuts):
   averageX, averageZ = AverageCutResiduals(dataFrame, cuts)
   #print(f'In Average Segmentation, array lengths: X : {np.shape(averageX)}, Z : {len(averageZ)}')
   #print(f'Average Values : X = {np.mean(averageX)}, Z = {np.mean(averageZ)}, First 5 X values: {averageX[:5]}, nans.. {np.argwhere(averageX == np.nan)} ')
   return np.mean(averageX[np.invert(np.isnan(averageX))]), np.mean(averageZ[np.invert(np.isnan(averageZ))])

def AverageCutResiduals(dataFrame, cuts):
   xResidualsCut = AddCutColumn(dataFrame, 'XResiduals', cuts[0], cuts[1])
   zResidualsCut = AddCutColumn(dataFrame, 'ZResiduals', cuts[2], cuts[3])

   AverageCutXResiduals = np.zeros(xResidualsCut.shape[0])
   AverageCutZResiduals = np.zeros(zResidualsCut.shape[0])
   for i in range(len(AverageCutXResiduals)):
      AverageCutXResiduals[i] = np.mean(np.abs(xResidualsCut[i]))
      AverageCutZResiduals[i] = np.mean(np.abs(zResidualsCut[i]))

   return AverageCutXResiduals, AverageCutZResiduals
def PlotResiduals(dataTracks, NumberOfEvents, data = ''):

   print(f'{'='*80}\nPlotting Residuals Start\n{'='*80}')

   xResiduals, zResiduals = CalculateResiduals(dataTracks)
   for i in range(NumberOfEvents):
      plt.figure()
      plt.scatter(dataTracks['X'].iloc[i], xResiduals[i], label = 'x residuals')
      plt.scatter(dataTracks['Z'].iloc[i], zResiduals[i], label = 'z residuals')
      plt.hlines([0]*80, xmin = 0, xmax = 125, alpha=0.25, linestyles='--')
      plt.xlabel('True position')
      plt.ylabel('Residuals')
      plt.legend()
      plt.title(f'Residuals of {i}th event')
      plt.savefig(f'JackData/{geometry}Residuals{i}thEvent{data}.png')

      plt.figure()
      plt.scatter(dataTracks['sigmaX'].iloc[i], xResiduals[i], label = 'x residuals')
      plt.scatter(dataTracks['sigmaZ'].iloc[i], zResiduals[i], label = 'z residuals')
      plt.hlines([0]*80, xmin = 0, xmax = 0.5, alpha=0.25, linestyles='--')
      plt.xlabel('Uncertainty')
      plt.ylabel('Residuals')
      plt.legend()
      plt.title(f'Uncertainty Residuals of {i}th event')
      plt.savefig(f'JackData/{geometry}UncertaintyResiduals{i}thEvent{data}.png')


      plt.figure()
      plt.scatter(dataTracks['X'].iloc[i], xResiduals[i]/dataTracks['sigmaX'].iloc[i], label = 'x residuals')
      plt.scatter(dataTracks['Z'].iloc[i], zResiduals[i]/dataTracks['sigmaZ'].iloc[i], label = 'z residuals')
      plt.hlines([1]*80, xmin = 20, xmax = 90, alpha=0.25, linestyles='--')
      plt.xlabel('True Position')
      plt.ylabel('Residuals/Uncertainty')
      plt.legend()
      plt.title(f'Percentage Residuals of {i}th event')
      plt.savefig(f'JackData/{geometry}PercentageResiduals{i}thEvent{data}.png')

   print(f'{'='*80}\nPlotting Residuals End\n{'='*80}')

def PlotFig(data, labels, filename, type, noBins = None, ranges = None):
   graphData = 0
   plt.figure()
   
   if type == 'scatter':
      plt.scatter(data[0], data[1])

   elif type == 'hist':
      graphData = plt.hist(data, bins = noBins, range = ranges)
      
   if type == '2scatters':
      plt.scatter(data[0], data[1], label = labels[3])
      plt.scatter(data[2], data[3], label = labels[4])
      plt.legend()

   elif type == '2hists':
      plt.hist(data[0], label = labels[3], bins = noBins)
      plt.hist(data[1], label = labels[4], bins = noBins)
      plt.legend()

   elif type == '2dhist':
      plt.hist2d(data[0], data[1], bins = noBins, cmap = 'viridis')
      plt.colorbar(label = 'Counts')

   elif type =='2errorbars':
      plt.errorbar(data[0], data[1], data[2], label = labels[3], fmt = 'b.')
      plt.errorbar(data[3], data[4], data[5], label = labels[4], fmt = 'r.')
      plt.legend()
   elif type =='errorbar':
         plt.errorbar(data[0], data[1], data[2], fmt = 'b.')
            
   plt.title(labels[0])
   plt.xlabel(labels[1])
   plt.ylabel(labels[2])
   plt.savefig(f'JackData/{filename}')
   return graphData

def CutCorrespondingColumn(dataFrame, targetColumn, referenceColumn, lowerLimit, upperLimit):
   cutArray = dataFrame.apply(
   lambda row: np.asarray(row[targetColumn])[
      (row[referenceColumn] >= lowerLimit) & (row[referenceColumn] <= upperLimit)
   ],
   axis=1
)
   return cutArray

def AddCutColumn(dataFrame, targetColumn, upperLimit, lowerLimit):
   cutArray = dataFrame[targetColumn].apply(
   lambda arr: [x for x in arr if lowerLimit <= x <= upperLimit]
)
   return cutArray

def Gaussian(x, mu, sigma, amp):
   return amp * np.exp((-1/2) * ((x-mu)/sigma)**2)

def DoubleGaussian(x, mu1, sigma1, amp1, mu2, sigma2, amp2):
   return amp1 * np.exp((-1/2) * ((x-mu1)/sigma1)**2) + amp2 * np.exp((-1/2) * ((x-mu2)/sigma2)**2)

def FitFunction(counts, binedges, function, initialGuesses):

   binCenters = (binedges[:-1] + binedges[1:]) / 2
   #print(f'Testing counts and bin edges : {np.max(counts)} and {binedges[:5]}, bin centres : {binCenters[:10]}')
   popt, pcov = curve_fit(function, binCenters, counts, initialGuesses)
   return popt[1], np.sqrt(np.diag(pcov))[1]
def main():

   analysisToRun = {'FlippedData':False, 'TrueData':False, 'SmearedData': False, '10Segments' : False, 'AllSegments' : True, 'Tracks8' : False}
   # First krakow data is 10 segments 

   ROOT.gSystem.Load("initial-proj/tpcTrackingAnalysis_build/libcentroid_data.so")
   ROOT.gSystem.Load("initial-proj/tpcTrackingAnalysis_build/libtrack_data.so")
   ROOT.gSystem.Load("initial-proj/tpcTrackingAnalysis_build/libtpc_dict.so")
   if analysisToRun['FlippedData']:
      print(f'{'='*80}\nFlipped Data Start\n{'='*80}')
      trackColumns = ["tpc.val", "tpc.channel", "tpc.row", "tpc.column", "tpc.timestamp", "tpc.pedestal", "tpc.peddev", "tpcT0"]
      _ ,_, flippedTracks = readFile(f'initial-proj/tpcTrackingAnalysis_build/tracks_centroids_{geometry}SortedFlipped.root', "trackingData", trackColumns, True)
      PlotFig((np.concatenate(flippedTracks['X']), np.concatenate(flippedTracks['Y'])), ('X vs Y Flipped Data', 'X (mm)', 'Y (mm)'), 'FlippedData/XYData', 'scatter')
      PlotFig((np.concatenate(flippedTracks['Z']), np.concatenate(flippedTracks['Y'])), ('Z vs Y Flipped Data', 'Z (mm)', 'Y (mm)'), 'FlippedData/ZYData', 'scatter')
      PlotFig((np.concatenate(flippedTracks['X']), np.concatenate(flippedTracks['Z'])), ('X vs Z Flipped Data', 'X (mm)', 'Z (mm)'), 'FlippedData/XZData', 'scatter')
      PlotFig((np.concatenate(flippedTracks['X']), np.concatenate(flippedTracks['Z'])), ('X vs Z Flipped Data', 'X (mm)', 'Z (mm)'), 'FlippedData/XZPositionsHist2D', '2dhist',100)

      flippedTracks['XResiduals'], flippedTracks['ZResiduals'] = CalculateResiduals(flippedTracks)
      AverageXResiduals, AverageZResiduals = AverageResiduals(flippedTracks)
      print(f'Length of array fed to plotting func: {len((np.concatenate(flippedTracks['ZResiduals'])))}')
      PlotFig((np.concatenate(flippedTracks['ZResiduals'])), ('Flipped Data Z Residuals', 'Residuals (mm)', 'Counts'), 'FlippedData/ZResiduals', 'hist', 100)
      PlotFig((np.concatenate(flippedTracks['XResiduals'])), ('Flipped Data X Residuals', 'Residuals (mm)', 'Counts'), 'FlippedData/XResiduals', 'hist', 100) 
      PlotFig((AverageXResiduals, flippedTracks['Chi2XY']), ('X \u03C7\u00B2 vs Average Residuals', 'Residuals (mm)', '\u03C7\u00B2'), 'FlippedData/chi2vsAverageResidualX', 'scatter')
      PlotFig((AverageZResiduals, flippedTracks['Chi2ZY']), ('Z \u03C7\u00B2 vs Average Residuals', 'Residuals (mm)', '\u03C7\u00B2'), 'FlippedData/chi2vsAverageResidualZ', 'scatter')
      PlotFig((AverageXResiduals, flippedTracks['points']), ('Hits vs Average X Residuals', 'Residuals (mm)', 'Hits'), 'FlippedData/hitsvsAverageResidualX', 'scatter')
      PlotFig((AverageZResiduals, flippedTracks['points']), ('Hits vs Average Z Residuals', 'Residuals (mm)', 'Hits'), 'FlippedData/hitsvsAverageResidualZ', 'scatter')

      PlotFig((flippedTracks['slopeXY']), ('XY Slope', 'Slope', 'Count'), 'FlippedData/XYSlope', 'hist', 50)
      PlotFig((flippedTracks['slopeZY']), ('ZY Slope', 'Slope', 'Count'), 'FlippedData/ZYSlope', 'hist', 50)
      PlotFig((flippedTracks['interceptXY']), ('XY Intercept', 'Intercept (mm)', 'Count'), 'FlippedData/XYIntercept', 'hist', 50)
      PlotFig((flippedTracks['interceptZY']), ('ZY Intercpet', 'Intercept (mm)', 'Count'), 'FlippedData/ZYIntercept', 'hist', 50)

      PlotFig((flippedTracks['slopeXY']), ('XY Slope Cut', 'Slope', 'Count'), 'FlippedData/XYSlopeCut', 'hist', 50, (-1,1))
      PlotFig((flippedTracks['slopeZY']), ('ZY Slope Cut', 'Slope', 'Count'), 'FlippedData/ZYSlopeCut', 'hist', 50, (-1,1))
      PlotFig((flippedTracks['interceptXY']), ('XY Intercept Cut', 'Intercept (mm)', 'Count'), 'FlippedData/XYInterceptCut', 'hist', 50, (0,500))
      PlotFig((flippedTracks['interceptZY']), ('ZY Intercept Cut', 'Intercept (mm)', 'Count'), 'FlippedData/ZYInterceptCut', 'hist', 50, (0,500))

      xSlopeCut = flippedTracks[(flippedTracks['slopeXY'] < 1) & (flippedTracks['slopeXY']>-1)]
      zSlopeCut = flippedTracks[(flippedTracks['slopeZY'] < 1) & (flippedTracks['slopeZY']>-1)]

      xInterceptCut = flippedTracks[(flippedTracks['interceptXY'] < 500) & (flippedTracks['interceptXY'] >0)]
      zInterceptCut = flippedTracks[(flippedTracks['interceptZY'] < 500) & (flippedTracks['interceptZY'] > 0)]

      print(f'Slopes cut :\nX = {flippedTracks.shape[0] - xSlopeCut.shape[0]}; Z = {flippedTracks.shape[0] - zSlopeCut.shape[0]}\nX = {flippedTracks.shape[0] - len(xInterceptCut)}; Z = {flippedTracks.shape[0] - len(zInterceptCut)}')

      flippedTracks['XResidualsCut'] = AddCutColumn(flippedTracks, 'XResiduals', 1, -1)
      flippedTracks['ZResidualsCut'] = AddCutColumn(flippedTracks, 'ZResiduals', 1, -1)
      flippedTracks['XCut'] = CutCorrespondingColumn(flippedTracks, 'X', 'XResiduals', -1, 1)
      flippedTracks['ZCut'] = CutCorrespondingColumn(flippedTracks, 'Z', 'ZResiduals', -1, 1)
            

      AverageCutXResiduals = np.zeros(flippedTracks.shape[0])
      AverageCutZResiduals = np.zeros(flippedTracks.shape[0])
      for i in range(len(AverageCutXResiduals)):
         AverageCutXResiduals[i] = np.mean(flippedTracks['XResidualsCut'].iloc[i])
         AverageCutZResiduals[i] = np.mean(flippedTracks['ZResidualsCut'].iloc[i])

      PlotFig((AverageCutXResiduals, flippedTracks['Chi2XY']), ('X \u03C7\u00B2 vs Average Cut Residuals', 'Residuals (mm)', '\u03C7\u00B2'), 'FlippedData/chi2vsAverageResidualXCut', 'scatter')
      PlotFig((AverageCutZResiduals, flippedTracks['Chi2ZY']), ('Z \u03C7\u00B2 vs Average Cut Residuals', 'Residuals (mm)', '\u03C7\u00B2'), 'FlippedData/chi2vsAverageResidualZCut', 'scatter')
      PlotFig((AverageCutXResiduals, flippedTracks['points']), ('Hits vs Average X Residuals', 'Residuals (mm)', 'Hits'), 'FlippedData/hitsvsAverageResidualXCut', 'scatter')
      PlotFig((AverageCutZResiduals, flippedTracks['points']), ('Hits vs Average Z Residuals', 'Residuals (mm)', 'Hits'), 'FlippedData/hitsvsAverageResidualZCut', 'scatter')

      """
      flippedTracks['XResidualsCut'] = CutCorrespondingColumn(flippedTracks, 'XResidualsCut', 'XCut', 0,50)
      flippedTracks['ZResidualsCut'] = CutCorrespondingColumn(flippedTracks, 'ZResidualsCut', 'ZCut', 0,50)
      flippedTracks['XCut'] = AddCutColumn(flippedTracks, 'XCut', 50,0)
      flippedTracks['ZCut'] = AddCutColumn(flippedTracks, 'ZCut', 50,0)
      """

      PlotFig((np.concatenate(flippedTracks['ZResidualsCut'])), ('Data Z Residuals Cut', 'Residuals (mm)', 'Counts'), 'FlippedData/ZResidualsCut', 'hist', 100)
      PlotFig((np.concatenate(flippedTracks['XResidualsCut'])), ('Data X Residuals Cut', 'Residuals (mm)', 'Counts'), 'FlippedData/XResidualsCut', 'hist', 100) 
      print(f'X values cut : {len(np.concatenate(flippedTracks['XResidualsCut'])) - len(np.concatenate(flippedTracks['XResiduals']))}, Z values cut : {len(np.concatenate(flippedTracks['ZResidualsCut'])) - len(np.concatenate(flippedTracks['ZResiduals']))}')
      print(f'Total data size = {len(np.concatenate(flippedTracks['XResiduals']))}, Number of tracks = {flippedTracks.shape[0]}')
      #PlotResiduals(flippedTracks, 5, 'Flipped')
      truePositionsCut = np.concatenate(flippedTracks['XCut'])
      truePositionsCut = np.append(truePositionsCut, np.concatenate(flippedTracks['ZCut']))
      trueResidualsCut = np.concatenate(flippedTracks['XResidualsCut'])
      trueResidualsCut = np.append(trueResidualsCut, np.concatenate(flippedTracks['ZResidualsCut']))

      PlotFig((truePositionsCut,trueResidualsCut), ('Residuals vs True Position (Cut)', 'True Position (mm)', 'Residual (mm)'), 'FlippedData/ResidualsVsTruePosCutHist2D', type = '2dhist', noBins = 500)
         
      print(f'{'='*80}\nFlipped Data End\n{'='*80}')

   if analysisToRun['TrueData']:
      print(f'{'='*80}\nTrue Simulated Data Start\n{'='*80}')

      trueColumns = ['ProtoTPC_Position_X', 'ProtoTPC_Position_Y', 'ProtoTPC_Position_Z']
      trueDF ,_, trueTracks = readFile(f'initial-proj/hibeam_g4_build/krakowTruth.root', "hibeam", trueColumns, False)
      print(f'True tracks columns: {trueDF.columns}, shape :  {trueDF.shape}')
      PlotFig((np.concatenate(trueDF['ProtoTPC_Position_X']), np.concatenate(trueDF['ProtoTPC_Position_Z'])), ['True X vs True Z (In ProtoTPC)', 'True X Position (cm)', 'True Z Postion (cm)'], 'TrueData/XvsZ', '2dhist', noBins = 100) 
      PlotFig((np.concatenate(trueDF['ProtoTPC_Position_X']), np.concatenate(trueDF['ProtoTPC_Position_Y'])), ['True X vs True Y (In ProtoTPC)', 'True X Position (cm)', 'True Y Postion (cm)'], 'TrueData/XvsY', '2dhist', noBins = 100) 
      PlotFig((np.concatenate(trueDF['ProtoTPC_Position_Z']), np.concatenate(trueDF['ProtoTPC_Position_Y'])), ['True Z vs True Y (In ProtoTPC)', 'True Z Position (cm)', 'True Y Postion (cm)'], 'TrueData/ZvsY', '2dhist', noBins = 100) 

      print(f'{'='*80}\nTrue Simulated Data End\n{'='*80}')

   if analysisToRun['SmearedData']:
      print(f'{'='*80}\nSmeared Simulated Data Start\n{'='*80}')

      smearedColumns = ['ProtoTPC.Pos_X', 'ProtoTPC.Pos_Z', 'ProtoTPC.Pos_Y']
      smearedDF ,_, trueTracks = readFile(f'initial-proj/hibeam_g4_analysis_build/krakowSmeared.root', "hibeam", smearedColumns, False)
      print(f'True tracks columns: {smearedDF.columns}, shape :  {smearedDF.shape}')
      PlotFig((np.concatenate(smearedDF['ProtoTPC.Pos_X']), np.concatenate(smearedDF['ProtoTPC.Pos_Z'])), ['Smeared X vs Smeared Z (In ProtoTPC)', 'Smeared X Position (cm)', 'Smeared Z Postion (cm)'], 'SmearedData/XvsZ', '2dhist', noBins = 100) 
      PlotFig((np.concatenate(smearedDF['ProtoTPC.Pos_X']), np.concatenate(smearedDF['ProtoTPC.Pos_Y'])), ['Smeared X vs Smeared Y (In ProtoTPC)', 'Smeared X Position (cm)', 'Smeared Y Postion (cm)'], 'SmearedData/XvsY', '2dhist', noBins = 100) 
      PlotFig((np.concatenate(smearedDF['ProtoTPC.Pos_Z']), np.concatenate(smearedDF['ProtoTPC.Pos_Y'])), ['Smeared Z vs Smeared Y (In ProtoTPC)', 'Smeared Z Position (cm)', 'Smeared Y Postion (cm)'], 'SmearedData/ZvsY', '2dhist', noBins = 100) 

      print(f'{'='*80}\nSmeared Simulated Data End\n{'='*80}')

   if analysisToRun['10Segments']:
      print(f'{'='*80}\nTracking Data 19 Start\n{'='*80}')
      
      trackColumns = ["tpc.val", "tpc.channel", "tpc.row", "tpc.column", "tpc.timestamp", "tpc.pedestal", "tpc.peddev", "tpcT0"]
      muonTracksDf,centroids, tracks = readFile(f'initial-proj/tpcTrackingAnalysis_build/tracks_centroids_{geometry}Sorted.root', "trackingData", trackColumns, True)

      print(f'{'='*80}\nPlotting Hits Start\n{'='*80}')
      print((tracks['sigmaX'] == 0).sum())
      #print(tracks['sigmaX'].iloc[np.argwhere(tracks['sigmaX'] == 0)])
      num_zeros = sum(np.sum(a == 0) for a in tracks['sigmaX'])
      print(num_zeros)
      all_sigmaX = np.concatenate(tracks['sigmaX'].values)

      print("Minimum sigmaX:", np.min(all_sigmaX))
      print("Smallest 10 sigmaX values:", np.sort(all_sigmaX)[:10])
      tracks['XResiduals'], tracks['ZResiduals'] = CalculateResiduals(tracks)
      tracks['XResiduals/Uncertainty'] = tracks.apply(
      lambda row: row['XResiduals'] / row['sigmaX'],
      axis=1
      )
      xHitCounts = np.concatenate(tracks['XResiduals/Uncertainty'].values)
      print(np.isinf(xHitCounts).sum())
      print(np.isnan(xHitCounts).sum())
      print(f'max X hit count: {max(xHitCounts[np.isfinite(xHitCounts)])}, min X hit count: {min(xHitCounts[np.isfinite(xHitCounts)])}')
      trueXHitCounts = xHitCounts[np.isfinite(xHitCounts)]
      print(f'Argwhere : {np.argwhere(trueXHitCounts >-10)[0][:]}')
      xLowCount = trueXHitCounts[np.argwhere(trueXHitCounts >-10).flatten()]
      xHighCount = xLowCount[np.argwhere(xLowCount < 10).flatten()]
      print(f'Points lost from cut = {len(xHighCount) - len(xHitCounts)}')
      print(f'Cut array shape: {np.shape(xHighCount)}, uncut array shape: {np.shape(xHitCounts)}, trueHitCounts : {np.shape(trueXHitCounts)}, low count : {np.shape(xLowCount)}')
      print(f'Cut data: {xHighCount}')

      PlotFig((xHitCounts[np.isfinite(xHitCounts)]), ('Residual/Uncertainty Hit Histogram (X)', 'X Residual/Uncertainty', 'Count'), 'HitHistogramX', 'hist')
      PlotFig((xHighCount), ('Residual/Uncertainty Hit Histogram (X) CUT', 'X Residual/Uncertainty', 'Count'), 'HitHistogramXCut', 'hist')


      tracks['ZResiduals/Uncertainty'] = tracks.apply(
      lambda row: row['ZResiduals'] / row['sigmaZ'],
      axis=1
      )
      zHitCounts = np.concatenate(tracks['ZResiduals/Uncertainty'].values)


      trueZHitCounts = zHitCounts[np.isfinite(zHitCounts)]
      zLowCount = trueZHitCounts[np.argwhere(trueZHitCounts >-10).flatten()]
      zHighCount = zLowCount[np.argwhere(zLowCount < 10).flatten()]
      print(f'Points lost from cut = {len(zHighCount) - len(zHitCounts)}')

      PlotFig((zHitCounts[np.isfinite(zHitCounts)]), ('Residual/Uncertainty Hit Histogram (Z)', 'Z Residual/Uncertainty', 'Count'), 'HitHistogramZ', 'hist')
      PlotFig((zHighCount), ('Residual/Uncertainty Hit Histogram (Z) CUT', 'Z Residual/Uncertainty', 'Count'), 'HitHistogramZCut', 'hist')

      print(f'{'='*80}\nPlotting Hits End\n{'='*80}')
      #TrackSlopeDistriution(tracks)

      xResiduals ,zResiduals = CalculateResiduals(tracks)
      xSigmas = np.concatenate(tracks['sigmaX'].values)
      zSigmas = np.concatenate(tracks['sigmaZ'].values)

      fig, axes = plt.subplots(2,2, figsize=(14,8))
      fig.tight_layout()
      axes[0,0].hist(np.concatenate(xResiduals))
      axes[0,0].set(ylabel = 'Count')
      axes[0,0].set_title('X Residuals')
      axes[0,1].hist(np.concatenate(zResiduals))
      axes[0,1].set_title('Z Residuals')
      axes[1,0].hist(xSigmas)
      axes[1,0].set(xlabel= 'Uncertainty', ylabel = 'Count')
      axes[1,0].set_title('X Uncertainties')
      axes[1,1].hist(zSigmas)
      axes[1,1].set(xlabel= 'Uncertainty')
      axes[1,1].set_title('Z Uncertainties')
      plt.savefig('JackData/Residuals&UncertaintiesHist.png')

      tracks['XResidualsCut'] = AddCutColumn(tracks, 'XResiduals', 1, -1)
      tracks['ZResidualsCut'] = AddCutColumn(tracks, 'ZResiduals', 1, -1)
      tracks['XCut'] = CutCorrespondingColumn(tracks, 'X', 'XResiduals', -1, 1)
      tracks['ZCut'] = CutCorrespondingColumn(tracks, 'Z', 'ZResiduals', -1, 1)
      tracks['XResidualsCut'] = CutCorrespondingColumn(tracks, 'XResidualsCut', 'XCut', 0,50)
      tracks['ZResidualsCut'] = CutCorrespondingColumn(tracks, 'ZResidualsCut', 'ZCut', 0,50)
      tracks['XCut'] = AddCutColumn(tracks, 'XCut', 50,0)
      tracks['ZCut'] = AddCutColumn(tracks, 'ZCut', 50,0)
      
      print(f'X residuals cut: {len(xResiduals) - len(np.concatenate(tracks['XResidualsCut']))}, Z residuals: {len(zResiduals) - len(np.concatenate(tracks['ZResidualsCut']))}')


      fig, (ax1,ax2) = plt.subplots(2)
      ax1.hist(np.concatenate(tracks['XResidualsCut']), range =(-1,1), bins = 100, label = 'X Residuals')
      ax2.hist(np.concatenate(tracks['ZResidualsCut']), range = (-1,1), bins = 100, label = 'z Residuals')
      #ax1.set_title('X Residuals (CUT)')
      ax1.set(xlabel='Residuals', ylabel='Count')
      #ax2.set_title('Z Residuals (CUT)')
      ax2.set(xlabel='Residuals')
      fig.suptitle('Cut Residuals')
      fig.legend()
      plt.savefig('JackData/Residuals&UncertaintyHistCut.png')
      
      PlotFig((np.concatenate(tracks['XResidualsCut'])), ('X Residuals (CUT)', 'Residuals (mm)', 'Counts'), 'XResidualsCut', type = 'hist')
      PlotFig((np.concatenate(tracks['ZResidualsCut'])), ('Z Residuals (CUT)', 'Residuals (mm)', 'Counts'), 'ZResidualsCut', type = 'hist')
      
      print(f'First 10 Anomalous values:\nSlope XY: {np.argwhere(tracks['slopeXY'] > 100)[:10]}\nIntercept XY: {np.argwhere(tracks['interceptXY'] < -5000)[:10]}\nSlope ZY: {np.argwhere(tracks['slopeZY'] > 1000)[:10]}\nIntercept ZY: {np.argwhere(tracks['interceptZY'] < -10000)[:10]}')

      fig, axes = plt.subplots(2,2, figsize=(12,8))
      axes[0,0].hist(tracks['slopeXY'])
      axes[0,0].set_title('XY slope')
      axes[0,0].set(ylabel='Count')
      axes[0,1].hist(tracks['slopeZY'])
      axes[0,1].set_title('ZY slope')
      axes[1,0].hist(tracks['interceptXY'])
      axes[1,0].set_title('XY Intercept')
      axes[1,0].set(ylabel='Count')
      axes[1,1].hist(tracks['interceptZY'])
      axes[1,1].set_title('ZY Intercept')
      plt.savefig('JackData/Slope&InterceptHist.png')

      xySlope = tracks['slopeXY'].to_numpy()
      zySlope = tracks['slopeZY'].to_numpy()
      xyIntercept = tracks['interceptXY'].to_numpy()
      zyIntercept = tracks['interceptZY'].to_numpy()

      fig, axes = plt.subplots(2,2, figsize=(12,8))
      axes[0,0].hist(xySlope[np.argwhere(xySlope<100)], range = (-1,1))
      axes[0,0].set_title('XY slope (CUT)')
      axes[0,0].set(ylabel='Count')
      axes[0,1].hist(zySlope[np.argwhere(zySlope<2000)], range = (-1,1))
      axes[0,1].set_title('ZY slope (CUT)')
      axes[1,0].hist(xyIntercept[np.argwhere(xyIntercept>-5000)], range = (0,50))
      axes[1,0].set_title('XY Intercept (CUT)')
      axes[1,0].set(ylabel='Count')
      axes[1,1].hist(zyIntercept[np.argwhere(zyIntercept>-10000)], range = (0,50))
      axes[1,1].set_title('ZY Intercept (CUT)')
      plt.savefig('JackData/Slope&InterceptHistCut.png')

      PlotFig((tracks['points'], tracks['Chi2XY'], tracks['points'], tracks['Chi2ZY']), ('\u03C7\u00B2 against Points', 'Number of Points', '\u03C7\u00B2', 'XY \u03C7\u00B2', 'ZY \u03C7\u00B2'), 'Chi2Plots', type = '2scatters')
      PlotFig((tracks['points'], tracks['Chi2XY']), ('X \u03C7\u00B2 against Points', 'Number of Points', '\u03C7\u00B2'), 'Chi2PlotsX', type = 'scatter')
      PlotFig((tracks['points'], tracks['Chi2ZY']), ('Z \u03C7\u00B2 against Points', 'Number of Points', '\u03C7\u00B2'), 'Chi2PlotsZ', type = 'scatter')

      

      AverageCutXResiduals = np.zeros(tracks.shape[0])
      AverageCutZResiduals = np.zeros(tracks.shape[0])
      for i in range(len(AverageCutXResiduals)):
         AverageCutXResiduals[i] = np.mean(tracks['XResidualsCut'].iloc[i])
         AverageCutZResiduals[i] = np.mean(tracks['ZResidualsCut'].iloc[i])

      #tempX = averageXResiduals[averageXResiduals>0.3845]
      #remainingX = tempX[tempX<0.3855]
      #tempZ = averageZResiduals[averageZResiduals>0.775]
      #remainingZ = tempZ[tempZ<0.785]


      xvalues, xcounts = np.unique(np.concatenate(tracks['XResidualsCut']), return_counts=True)
      peak_x = xvalues[np.argmax(xcounts)]  
      zvalues, zcounts = np.unique(np.concatenate(tracks['ZResidualsCut']), return_counts=True)
      peak_z = zvalues[np.argmax(zcounts)]  
      print(f'Peaks are at : {peak_x} for X, {peak_z} for Z')
      
      #print(f'Entries at 0.385 : {len(remainingX)}, and at 0.78 : {len(remainingZ)}')

      PlotFig((AverageCutXResiduals, tracks['Chi2XY'], AverageCutZResiduals, tracks['Chi2ZY']), ('\u03C7\u00B2 against Average Residuals', 'Average Residuals (cm)', '\u03C7\u00B2', 'XY \u03C7\u00B2', 'ZY \u03C7\u00B2'), 'Chi2ResidualsPlots', type = '2scatters')
      PlotFig((AverageCutXResiduals, tracks['Chi2XY']), ('X \u03C7\u00B2 against Average Residuals', 'Average Residuals (cm)', '\u03C7\u00B2'), 'Chi2XResidualsPlots', 'scatter')
      PlotFig((AverageCutZResiduals, tracks['Chi2ZY']), ('Z \u03C7\u00B2 against Average Residuals', 'Average Residuals (cm)', '\u03C7\u00B2'), 'Chi2ZResidualsPlots', 'scatter')
      
      PlotFig((AverageCutXResiduals, tracks['points']), ('Track Hits vs Average X Residuals', 'Average Residuals (cm)', 'Number of hits'), 'Chi2XResidualsPlots', type = 'sactter')
      PlotFig((AverageCutZResiduals, tracks['points']), ('Track Hits vs Average Z Residuals', 'Average Residuals (cm)', 'Number of hits '), 'Chi2ZResidualsPlots', type = 'sactter')

      print(f'Entries with > 10 hits: {tracks[tracks['points'] == 11].shape[0]}')
      
      PlotFig((np.concatenate(tracks['X']), np.concatenate(tracks['XResiduals']), np.concatenate(tracks['Z']), np.concatenate(tracks['ZResiduals'])), ('Residuals vs True Position', 'True Position (mm)', 'Residuals (mm)', 'X Residuals', 'Z Residuals'), 'ResidualsVsTruePos', type = '2satters')
      PlotFig((np.concatenate(tracks['X']), np.concatenate(tracks['XResiduals'])), ('X Residuals vs True Position', 'True Position (mm)', 'Residuals (mm)'), 'ResidualsVsTruePosX', type = 'scatter')
      PlotFig((np.concatenate(tracks['Z']), np.concatenate(tracks['ZResiduals'])), ('Z Residuals vs True Position', 'True Position (mm)', 'Residuals (mm)'), 'ResidualsVsTruePosZ', type = 'scatter')

      PlotFig((np.concatenate(tracks['XCut']), np.concatenate(tracks['XResidualsCut']), np.concatenate(tracks['ZCut']), np.concatenate(tracks['ZResidualsCut'])), ('Residuals vs True Position (Cut)', 'True Position (mm)', 'Residuals (mm)', 'X Residuals', 'Z Residuals'), 'ResidualsVsTruePosCut', type = '2scatters')

      truePositionsCut = np.concatenate(tracks['XCut'])
      truePositionsCut = np.append(truePositionsCut, np.concatenate(tracks['ZCut']))
      trueResidualsCut = np.concatenate(tracks['XResidualsCut'])
      trueResidualsCut = np.append(trueResidualsCut, np.concatenate(tracks['ZResidualsCut']))

      PlotFig((truePositionsCut,trueResidualsCut), ('Residuals vs True Position (Cut)', 'True Position (cm)', 'Residual (cm)'), 'ResidualsVsTruePosCutHist2D', type = '2dhist', noBins = 100)
      PlotFig((np.concatenate(tracks['XCut']), np.concatenate(tracks['XResidualsCut'])), ('2D Hist X Residuals vs True Position', 'True Position (cm)', 'Residual (cm)'), 'ResidualsVsTruePosXCutHist2DTruePosCut', type = '2dhist', noBins = 100)
      PlotFig((np.concatenate(tracks['ZCut']), np.concatenate(tracks['ZResidualsCut'])), ('2D Hist Z Residuals vs True Position', 'True Position (cm)', 'Residual (cm)'), 'ResidualsVsTruePosZCutHist2DTruePosCut', type = '2dhist', noBins = 100)
      PlotFig((np.concatenate(tracks['X']), np.concatenate(tracks['Z'])), ('X vs Z True Position', 'X True Position', 'Z True Position'), 'TruePositionsHist2D', type = '2dhist', noBins = 100)

      totalHits = np.concatenate(tracks['X'])
      totalHits = np.append(totalHits, np.concatenate(tracks['Z']))
      print(f'Final number of cut events : {len(totalHits) - len(truePositionsCut)}, Total events left : {len(trueResidualsCut)} \nCut X values : {len(np.concatenate(tracks['X'])) - len(np.concatenate(tracks['XCut']))}, x values left : {len(np.concatenate(tracks['XCut']))}\nCut Z values : {len(np.concatenate(tracks['Z'])) - len(np.concatenate(tracks['ZCut']))}')
      print(f'{'='*80}\nTracking Data 19 End\n{'='*80}')

   
   if analysisToRun['Tracks8']:
      trackColumns = ["tpc.val", "tpc.channel", "tpc.row", "tpc.column", "tpc.timestamp", "tpc.pedestal", "tpc.peddev", "tpcT0"]
      
      _, _, tracks8 = readFile(f'initial-proj/tpcTrackingAnalysis_build/tracks_centroids_{geometry}SortedFlipped.root', "trackingData", trackColumns, True)
      print(f'2 segment shape: {tracks8.shape[0]}')
      tracks8['XResiduals'], tracks8['ZResiduals'] = CalculateResiduals(tracks8)

      tracks8['ZCut'] = CutCorrespondingColumn(tracks8, 'Z', 'ZResiduals', -1, 1 )
      tracks8['predictedZCut'] = CutCorrespondingColumn(tracks8, 'predictedZ', 'ZResiduals', -1,1 )
      tracks8['ZYSlopes'] = [[slope] * len(np.asarray(z)) for slope, z in zip(tracks8['slopeZY'],tracks8['Z'])]
      tracks8['ZYIntercepts'] = [[intercept] * len(np.asarray(z)) for intercept, z in zip(tracks8['interceptZY'],tracks8['Z'])]
      tracks8['slopeZYCut'] = CutCorrespondingColumn(tracks8, 'ZYSlopes', 'ZResiduals', -1,1 )
      tracks8['interceptZYCut'] = CutCorrespondingColumn(tracks8, 'ZYIntercepts', 'ZResiduals', -1, 1 )
      tracks8['ZResidualsCut'] = AddCutColumn(tracks8, 'ZResiduals', 1, -1)
      
      PlotFig((np.concatenate(tracks8['Z']), np.concatenate(tracks8['ZResiduals'])), ('Z Residuals vs Smeared Z', 'Smeared Z', 'Z Residuals'), 'SegmentationData/ZResvsZSmeared', '2dhist', 100)
      PlotFig((np.concatenate(tracks8['predictedZ']), np.concatenate(tracks8['ZResiduals'])), ('Z Residuals vs Predicted Z', 'Predicted Z', 'Z Residuals'), 'SegmentationData/ZResvsZPredicted', '2dhist', 100)
      PlotFig((np.concatenate(tracks8['ZYSlopes']), np.concatenate(tracks8['ZResiduals'])), ('Z Residuals vs ZY Slope', 'ZY Slope', 'Z Residuals'), 'SegmentationData/ZResvsZYSlope', '2dhist', 100)
      PlotFig((np.concatenate(tracks8['ZYIntercepts']), np.concatenate(tracks8['ZResiduals'])), ('Z Residuals vs ZY Intercept', 'ZY Intercept', 'Z Residuals'), 'SegmentationData/ZResvsZYIntercept', '2dhist', 100)

      PlotFig((np.concatenate(tracks8['ZCut']), np.concatenate(tracks8['ZResidualsCut'])), ('Z Residuals vs Smeared Z (Cut)', 'Smeared Z', 'Z Residuals'), 'SegmentationData/ZResvsZSmearedCut', '2dhist', 100)
      PlotFig((np.concatenate(tracks8['predictedZCut']), np.concatenate(tracks8['ZResidualsCut'])), ('Z Residuals vs Predicted Z (Cut)', 'Predicted Z', 'Z Residuals'), 'SegmentationData/ZResvsZPredictedCut', '2dhist', 100)
      PlotFig((np.concatenate(tracks8['slopeZYCut']), np.concatenate(tracks8['ZResidualsCut'])), ('Z Residuals vs ZY Slope (Cut)', 'ZY Slope', 'Z Residuals'), 'SegmentationData/ZResvsZYSlopeCut', '2dhist', 100)
      PlotFig((np.concatenate(tracks8['interceptZYCut']), np.concatenate(tracks8['ZResidualsCut'])), ('Z Residuals vs ZY Intercept (Cut)', 'ZY Intercept', 'Z Residuals'), 'SegmentationData/ZResvsZYInterceptCut', '2dhist', 100)

      tracks8['XResidualsCut'] = AddCutColumn(tracks8, 'XResiduals', 1, -1)
      histData = PlotFig(np.concatenate(tracks8['XResidualsCut']), ('X Residuals 8 Segments', 'Residuals (cm)', 'Counts'), 'SegmentationData/XResiduals10segments', 'hist', noBins= 100)
      counts = histData[0]
      binedges = histData[1]
      binCenters = (binedges[:-1] + binedges[1:]) / 2
      print(f'Testing counts and bin edges : {np.max(counts)} and {binedges[:5]}, bin centres : {binCenters[:10]}')
      popt, pcov = curve_fit(Gaussian, binCenters, counts, (0, 0.5, 50000))
      print(f'Fitted params: mu {popt[0]}, sigma {popt[1]}, amp {popt[2]}')
      
      predictedCounts = Gaussian(np.linspace(-1, 1, 100), *popt)

      plt.figure()
      plt.hist(np.concatenate(tracks8['XResidualsCut']), bins = 100, label = 'Simulated Data')
      plt.plot(np.linspace(-1, 1, 100), predictedCounts, label = 'Fitted')
      plt.title('Fitted X Residuals')
      plt.xlabel('Residuals')
      plt.ylabel('Counts')
      plt.legend()
      plt.savefig('JackData/SegmentationData/FittedXResiduals10')

      tracks8['ZResidualsCut'] = AddCutColumn(tracks8, 'ZResiduals', 5, -5)
      histData = PlotFig(np.concatenate(tracks8['ZResidualsCut']), ('Z Residuals 8 Segments', 'Residuals (cm)', 'Counts'), 'SegmentationData/ZResiduals10segments', 'hist', noBins= 100)
      counts = histData[0]
      binedges = histData[1]
      binCenters = (binedges[:-1] + binedges[1:]) / 2
      #print(f'Testing counts and bin edges : {np.max(counts)} and {binedges[:5]}, bin centres : {binCenters[:10]}')
      fullPopt, fullPcov = curve_fit(Gaussian, binCenters, counts, (0, 4, 20000))
      #print(f'Fitted params: mu {popt[0]}, sigma {popt[1]}, amp {popt[2]}')
      zFittingRange = np.linspace(-5, 5, 1000)
      fullPredictedCounts = Gaussian(zFittingRange, *fullPopt)

      doublePopt, doublePcov = curve_fit(DoubleGaussian, binCenters, counts, (0,2, 30000, 2, 0.1, 100)) #(0, 4, 20000, 0, 0.1, 100))
      #print(f'Fitted params: mu {popt[0]}, sigma {popt[1]}, amp {popt[2]}')
      
      doubleGausPredictedCounts = DoubleGaussian(zFittingRange, *doublePopt)

      print(f'argwhere output : {np.argwhere(binCenters<2)}, [0] output : {np.argwhere(binCenters<2)[0]}')
      restrictedPopt, restrictedPcov = curve_fit(Gaussian, binCenters[binCenters<2], counts[binCenters<2], (0, 4, 20000))
      #print(f'Fitted params: mu {popt[0]}, sigma {popt[1]}, amp {popt[2]}')
      
      restrictedPredictedCounts = Gaussian(zFittingRange, *restrictedPopt)
      
      print(f"Fitted \u03C3's : full Gaussian : {fullPopt[1]} \u00B1 {np.sqrt(np.diag(fullPcov))[1]}, double Gaussian : {doublePopt[1]} \u00B1 {np.sqrt(np.diag(doublePcov))[1]}, restricted Gaussian : {restrictedPopt[1]} \u00B1 {np.sqrt(np.diag(restrictedPcov))[1]}")
      
      plt.figure()
      plt.hist(np.concatenate(tracks8['ZResidualsCut']), bins = 100, label = 'Simulated Data')
      plt.plot(zFittingRange, fullPredictedCounts, label = 'Gaussian Full Range')
      plt.plot(zFittingRange, restrictedPredictedCounts, label = 'Gaussian Restricted Range')
      plt.plot(zFittingRange, doubleGausPredictedCounts, label = 'Double Gaussian Full Range')
      plt.title('Fitted Z Residuals')
      plt.xlabel('Residuals')
      plt.ylabel('Counts')
      plt.legend(loc = 'upper left')
      plt.savefig('JackData/SegmentationData/FittedZResiduals10')

      fig, axes = plt.subplots(2,2, figsize=(12,8), constrained_layout=True)
      axes[0,0].hist(tracks8['slopeXY'], range = (-1,1), bins = 50)
      axes[0,0].set_title('XY slope')
      axes[0,0].set(ylabel='Count', xlabel = 'Slope')
      axes[0,1].hist(tracks8['slopeZY'], range = (-1,1), bins = 50)
      axes[0,1].set_title('ZY slope')
      axes[0,1].set(ylabel='Count', xlabel = 'Slope')
      axes[1,0].hist(tracks8['interceptXY'], range = (-50,150), bins = 50)
      axes[1,0].set_title('XY Intercept')
      axes[1,0].set(ylabel='Count', xlabel = 'Intercept (mm)')
      axes[1,1].hist(tracks8['interceptZY'], range = (0,500), bins = 50)
      axes[1,1].set_title('ZY Intercept')
      axes[1,1].set(ylabel='Count', xlabel = 'Intercept (mm)')
      plt.savefig('JackData/SegmentationData/SlopesAndIntercepts')

   if analysisToRun['AllSegments']:

      print(f'{'='*80}\nReading Data Start\n{'='*80}')

      trackColumns = ["tpc.val", "tpc.channel", "tpc.row", "tpc.column", "tpc.timestamp", "tpc.pedestal", "tpc.peddev", "tpcT0"]

      segmentations = [4, 6, 8, 10, 12, 14, 16, 18, 20]
      tracks = []

      desiredColumns = ['slopeXYErr', 'slopeZYErr', 'interceptXYErr', 'interceptZYErr']
      tracks.append(readFile(f'initial-proj/tpcTrackingAnalysis_build/tracks_centroids_{geometry}4Sorted.root', "trackingData", trackColumns, True)[2])
      tracks.append(readFile(f'initial-proj/tpcTrackingAnalysis_build/tracks_centroids_{geometry}6Sorted.root', "trackingData", trackColumns, True)[2])
      tracks.append(readFile(f'initial-proj/tpcTrackingAnalysis_build/tracks_centroids_{geometry}8Sorted.root', "trackingData", trackColumns, True)[2])
      tracks.append(readFile(f'initial-proj/tpcTrackingAnalysis_build/tracks_centroids_{geometry}SortedFlipped.root', "trackingData", trackColumns, True)[2])
      tracks.append(readFile(f'initial-proj/tpcTrackingAnalysis_build/tracks_centroids_{geometry}12Sorted.root', "trackingData", trackColumns, True)[2])
      tracks.append(readFile(f'initial-proj/tpcTrackingAnalysis_build/tracks_centroids_{geometry}14Sorted.root', "trackingData", trackColumns, True)[2])
      tracks.append(readFile(f'initial-proj/tpcTrackingAnalysis_build/tracks_centroids_{geometry}16Sorted.root', "trackingData", trackColumns, True)[2])
      tracks.append(readFile(f'initial-proj/tpcTrackingAnalysis_build/tracks_centroids_{geometry}18Sorted.root', "trackingData", trackColumns, True)[2])
      tracks.append(readFile(f'initial-proj/tpcTrackingAnalysis_build/tracks_centroids_{geometry}20Sorted.root', "trackingData", trackColumns, True)[2])
      
      for i in tracks :
         i['XResiduals'], i['ZResiduals'] = CalculateResiduals(i)

      
      print(f'{'='*80}\nData Analysis\n{'='*80}')

      for i in range(len(tracks)):
         PlotFig((np.concatenate(tracks[i]['X']), np.concatenate(tracks[i]['predictedX'])), (f'Predicted Z vs Smeared Z ({segmentations[i]} Segments)', 'Smeared Z', 'Predicted Z'), f'3HitSegmentData/PredictedvsSmearedZ{segmentations[i]}Segments', 'scatter')
         PlotFig((np.concatenate(tracks[i]['Z']), np.concatenate(tracks[i]['predictedZ'])), (f'Predicted Z vs Smeared Z ({segmentations[i]} Segments)', 'Smeared Z', 'Predicted Z'), f'3HitSegmentData/PredictedvsSmearedZ{segmentations[i]}Segments2Dhist', '2dhist', noBins = 100)
         PlotFig(np.concatenate(tracks[i]['XResiduals']), (f'X Residuals {segmentations[i]} Segments', 'Residuals (cm)', 'Counts'), f'SegmentationData/XResiduals{segmentations[i]}segments', 'hist', noBins= 100)
         PlotFig(np.concatenate(tracks[i]['ZResiduals']), (f'Z Residuals {segmentations[i]} Segments', 'Residuals (cm)', 'Counts'), f'SegmentationData/ZResiduals{segmentations[i]}segments', 'hist', noBins= 100)

      zCuts = (5, -5)
      xCuts = (1, -1)

      print(f'{'='*80}\nStarting Residuals Analysis\n{'='*80}')

      xHists = []
      zHists = []
      for i in range(len(tracks)):
         tracks[i]['XResidualsCut'] = AddCutColumn(tracks[i], 'XResiduals', xCuts[0], xCuts[1])
         tracks[i]['ZResidualsCut'] = AddCutColumn(tracks[i], 'ZResiduals', zCuts[0], zCuts[1])
      
      for i in range(len(tracks)):
         xHists.append(PlotFig(np.concatenate(AddCutColumn(tracks[i], 'XResiduals', xCuts[0], xCuts[1])), (f'X Residuals {segmentations[i]} Segments (Cut)', 'Residuals (cm)', 'Counts'), f'3HitSegmentData/XResiduals{segmentations[i]}segmentscut', 'hist', noBins= 100))
         zHists.append(PlotFig(np.concatenate(AddCutColumn(tracks[i], 'ZResiduals', zCuts[0], zCuts[1])), (f'Z Residuals {segmentations[i]} Segments (Cut)', 'Residuals (cm)', 'Counts'), f'3HitSegmentData/ZResiduals{segmentations[i]}segmentscut', 'hist', noBins= 100))
   
      XWidths = np.zeros(len(segmentations))
      XErrs = np.zeros(len(segmentations))
      ZWidths = np.zeros(len(segmentations))
      ZErrs = np.zeros(len(segmentations))

      for i in range(len(segmentations)):
         XWidths[i], XErrs[i] = FitFunction(xHists[i][0], xHists[i][1], Gaussian, (0,0.5, 40000))
         ZWidths[i], ZErrs[i] = FitFunction(zHists[i][0], zHists[i][1], DoubleGaussian, (0,4, 20000, 2, 0.1, 100))
      
      PlotFig((segmentations, np.abs(XWidths), XErrs, segmentations, ZWidths, ZErrs), ('Widths vs Segmentation', 'Segmentation', 'Width', 'X', 'Z'), '3HitSegmentData/WidthvsSegementation', '2errorbars')
      PlotFig((segmentations, np.abs(XWidths), XErrs), ('X Widths vs Segmentation', 'Segmentation', 'Width'), '3HitSegmentData/WidthvsSegementationX', 'errorbar')
      PlotFig((segmentations, np.abs(ZWidths), ZErrs), ('Z Widths vs Segmentation', 'Segmentation', 'Width'), '3HitSegmentData/WidthvsSegementationZ', 'errorbar')
      print(f'Calculated Widths:\nX Widths: {np.abs(XWidths)}\nZ Widths: {ZWidths}')
      #### Predicting positions - fist step is to find centroids which have tracks, i.e. events with >7 
      #PlotResiduals(tracks, 10)
      print(f'{'='*80}\nFinished Residuals Analysis\n{'='*80}') 
      #segmentations = [8, 10, 12, 14, 16, 18]
      AverageXResidualsArray = np.zeros(len(segmentations))
      AverageZResidualsArray = np.zeros(len(segmentations))

      for i in range(len(tracks)):
         AverageXResidualsArray[i], AverageZResidualsArray[i] = AverageCutResidualsSegmentation(tracks[i], (1,-1, zCuts[0], zCuts[1]))
      print(f'Average X values : {AverageXResidualsArray}\nAverage Z values : {AverageZResidualsArray}')
      
      PlotFig((segmentations, AverageXResidualsArray, segmentations, AverageZResidualsArray), ('Average Residual vs Segmentation', 'Segmentation', 'Average Residual (cm)', 'X', 'Z'), f'3HitSegmentData/{geometry}SegmentationAverageResiduals', '2scatters')
      
      averageHits  = np.zeros(len(segmentations))
      for i in range(len(segmentations)):
         averageHits[i] = np.mean(tracks[i]['points'])
      PlotFig((segmentations, averageHits), ('Average hit number vs Segmentation', 'Segments', 'Average hit per Track'), '3HitSegmentData/AverageHitvsSegment', 'scatter')
      print(f'Hit averages : {averageHits}')
   
      titles = ['slopeXY', 'slopeZY', 'interceptXY', 'interceptZY']
      limits = ((-1, 1), (-1, 1), (-50, 150), (0, 500))
      cuts = [[],[],[],[]]
      for i in range(len(segmentations)):
         for j in range(len(titles)):
            mask = ((tracks[i][f'{titles[j]}'] < limits[j][0]) |(tracks[i][f'{titles[j]}'] > limits[j][1]))

            print("Values being removed:", mask.sum())
            #print(tracks[i].loc[mask, f'{titles[j]}'].head())

            tracks[i][f'{titles[j]}Cut'] = tracks[i][f'{titles[j]}'].iloc[mask]
            tracks[i].loc[mask, f'{titles[j]}'] = None
            tracks[i].loc[mask, f'{titles[j]}Err'] = None
            #tracks[i][f'{titles[j]}Cut'] = tracks[i][f'{titles[j]}'].where(tracks[i][f'{titles[j]}'].between(limits[j][0], limits[j][1]),None)
            print(f'Number of {titles[j]} points cut {segmentations[i]} segments: {len(tracks[i][f'{titles[j]}']) - len(tracks[i][f'{titles[j]}Cut'])}, Low Limit = {limits[j][0]}, Upper Limit = {limits[j][1]}')
      for i in range(len(segmentations)):
               PlotFig((tracks[i]['interceptXY']), (f'InterceptXY distribution {segmentations[i]} segments', 'Intercept (cm)', 'Counts'), f'3HitSegmentData/XYIntercepts{segmentations[i]}segs', 'hist', noBins= 40)
               PlotFig((tracks[i]['interceptZY']), (f'interceptZY distribution {segmentations[i]} segments', 'Intercept (cm)', 'Counts'), f'3HitSegmentData/ZYIntercepts{segmentations[i]}segs', 'hist', noBins= 40)
               PlotFig((tracks[i]['slopeXY']), (f'SlopeXY distribution {segmentations[i]} segments', 'Slope', 'Counts'), f'3HitSegmentData/XYSlopes{segmentations[i]}segs', 'hist', noBins= 40)
               PlotFig((tracks[i]['slopeZY']), (f'SlopeZY distribution {segmentations[i]} segments', 'Slope', 'Counts'), f'3HitSegmentData/ZYSlopes{segmentations[i]}segs', 'hist', noBins= 40)
      #tracks[0]['interceptXYCut'] = tracks[0][tracks[0]['intceptXY'] <1]['interceptXY']
      
      slopesAndIntercepts = [np.zeros(len(segmentations)), np.zeros(len(segmentations)), np.zeros(len(segmentations)), np.zeros(len(segmentations))]
      slopesAndInterceptsErrs = [np.zeros(len(segmentations)), np.zeros(len(segmentations)), np.zeros(len(segmentations)), np.zeros(len(segmentations))]

      for i in range(len(segmentations)):
         for j in range(len(titles)):
            slopesAndIntercepts[j][i] = np.mean(tracks[i][f'{titles[j]}'])
            slopesAndInterceptsErrs[j][i] = np.sqrt(np.nansum(tracks[i][f'{titles[j]}Err']**2)/len(tracks[i].dropna(subset=f'{titles[j]}')))
         #slopesAndIntercepts[1][i] = np.mean(tracks[i]['slopeZY'])
         #slopesAndIntercepts[2][i] = np.mean(tracks[i]['interceptXY'])
         #slopesAndIntercepts[3][i] = np.mean(tracks[i]['interceptZY'])
      print(f'Erorrs are : {slopesAndInterceptsErrs}')
      desiredColumns = ['slopeXYErr', 'slopeZYErr', 'interceptXYErr', 'interceptZYErr']
      units = ['','','(mm)','(mm)']
      print(f'20 segment errors : {tracks[-1][desiredColumns].head()}')
      print(f'20 Segments values : \nMax error : {max(tracks[-1]['interceptXYErr'])} \nIntercept with max error : {tracks[-1].loc[np.argmax(tracks[-1]['interceptXYErr']), 'interceptXY']}\nnansum : {np.nansum(tracks[-1]['interceptXYErr']**2)} \nDivided sum {np.nansum(tracks[-1]['interceptXYErr']**2)/len(tracks[i].dropna(subset=f'{titles[j]}'))}\n Length of tracks {len(tracks[i].dropna(subset=f'{titles[j]}'))} \nTotal error : {np.sqrt(np.nansum(tracks[-1]['interceptXYErr']**2)/len(tracks[i].dropna(subset=f'{titles[j]}')))}')
      fig, axes = plt.subplots(2,2, figsize=(12,8), constrained_layout=True)
      xplot = [0,0,1,1]
      yplot = [0,1,0,1]
      for i in range(len(titles)):
            axes[xplot[i], yplot[i]].errorbar(segmentations, slopesAndIntercepts[i], slopesAndInterceptsErrs[i], fmt = 'b.')
            axes[xplot[i], yplot[i]].set_title(f'Average {titles[i]} vs Segmentation')
            axes[xplot[i], yplot[i]].set(ylabel = f'{titles[i][:-2]} {units[i]}', xlabel = 'Segmentation')
      plt.savefig('JackData/3HitSegmentData/SlopesAndIntercepts')
      for i in range(len(titles)):
         PlotFig((segmentations, slopesAndIntercepts[i], slopesAndInterceptsErrs[i]), (f'Average {titles[i]} vs Segmentation', 'Segmentation', f'{titles[i][:-2]} {units[i]}'), f'3HitSegmentData/Average{titles[i]}PerSegment', 'errorbar')
if __name__ == "__main__":
    main()