#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  UBID_Encoder.py
#  
#  Copyright 2020 Andrew.Held <Andrew.Held@DOEE-1Z836H2>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  
import xml.etree.ElementTree as Et
import array, xlrd, csv, os, smtplib, time, logging, json, datetime
from ast import literal_eval
import multiprocessing
import numpy as np
import pandas as pd
from datetime import timedelta
from functools import partial
from time import sleep
import buildingid.code


filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'UBID.log')
logging.basicConfig(filename=filename, level=logging.DEBUG, filemode='w')
 


def main(args):
    return 0


if __name__ == '__main__':
	import sys
	def createFolder(directory):
		try:
			if not os.path.exists(directory):
				os.makedirs(directory)
		except OSError:
			print ('Error: Creating directory. ' +  directory)
	
	createFolder('./Output/')
	ts =  time.gmtime()
	tstamp =  (time.strftime("%Y%m%d_%H%M%S", ts))
	tstamp2 = (time.strftime("%m/%d/%y %H:%M:%S %p", ts))
	building_Join = pd.read_excel('v1FinalJoin_Building_Lot_10percent\\Final_UBID_10p_20201023.xlsx')
	print
	building_Join['nSSL'] = building_Join.groupby(['SSL'])['Min_Lat'].transform('count')
	print (building_Join['nSSL'])

	building_Join_2 = building_Join.set_index(building_Join.columns.drop('SSL',1).tolist())['SSL'].str.split(';',expand=True).stack().reset_index().rename(columns ={0:'SSL'}).loc[:, building_Join.columns]
	building_Join_2['UBID'] = building_Join_2.apply(lambda row: buildingid.code.encode(latitudeLo = row['Min_Lat'], longitudeLo= row['Min_Long'], latitudeHi= row['Max_Lat'], longitudeHi= row['Max_Long'],latitudeCenter= row['Centroid_Y'], longitudeCenter= row['Centroid_X'], codeLength = 11),axis = 1)

	#for index, row in building_Join_2.iterrows():
		#building_Join_2.loc[index,'UBID'] = buildingid.code.encode(latitudeLo = row['Min_Lat'], longitudeLo= row['Min_Long'], latitudeHi= row['Max_Lat'], longitudeHi= row['Max_Long'],latitudeCenter= row['Centroid_Y'], longitudeCenter= row['Centroid_X'], codeLength = 11)
	
	#building_Join = building_Join['SSL'].str.split(';').tolist(), index=building_Join['UBID']).stack()
	#building_Join = building_Join.reset_index()
	building_Join_2['nUBID'] = building_Join_2.groupby(['UBID'])['Min_Lat'].transform('count')
	building_Join_2.loc[(building_Join_2['nUBID'] == 1) & (building_Join_2['nSSL'] == 1), 'Link_Type'] = 1
	building_Join_2.loc[(building_Join_2['nUBID'] > 1) & (building_Join_2['nSSL'] == 1), 'Link_Type'] = 2
	building_Join_2.loc[(building_Join_2['nUBID'] == 1) & (building_Join_2['nSSL'] > 1), 'Link_Type'] = 3
	building_Join_2.loc[(building_Join_2['nUBID'] > 1) & (building_Join_2['nSSL'] > 1), 'Link_Type'] = 4
	
	building_Join_2.loc[(building_Join_2['Link_Type'] == 1), 'Link_Type_Description'] = 'One Building One Lot'
	building_Join_2.loc[(building_Join_2['Link_Type'] == 2), 'Link_Type_Description'] = 'Many Buildings One Lot'
	building_Join_2.loc[(building_Join_2['Link_Type'] == 3), 'Link_Type_Description'] = 'One Building Many Lots'
	building_Join_2.loc[(building_Join_2['Link_Type'] == 4), 'Link_Type_Description'] = 'Many Buildings Many Lots'

		
	building_Join_2.to_excel('Output\\UBIDs_'+tstamp+'.xlsx')
	sys.exit(main(sys.argv))
