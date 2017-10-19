#!/usr/bin/python


from lxml import html
import requests
import urllib
import sys

class BoatList:
	'Search for boats by VRN or name and hold the resulting list'
	base_url = 'http://www-ops2.pac.dfo-mpo.gc.ca/vrnd-rneb/'
#	base_url = 'http://ww-ops2.pac.dfo-mpo.gc.ca/vrnd-rneb/'
	search_url = 'index-eng.cfm?pg=VesselSearchResult'
	headers = {'User-Agent': 'Mozilla/5.0'}


	def __init__(self, search_vrn='0', search_name=''):
		self.vrn = search_vrn
		self.name = search_name.upper()
		self.boat_list = []
		self.dot = ''
		self.surveyed = ''
		self.survey_date = ''
		self.search_status = ''

	def searchByVRN(self):
		values = {'VRNid':self.vrn}
		return self.performSearch(values)

	def searchByName(self):
		values = {'VslName':self.name}
		return self.performSearch(values)

	def performSearch(self, post_values):
		url = BoatList.base_url + BoatList.search_url
		try:
			res = requests.post(url, headers=BoatList.headers, data=post_values)
		except:
			print 'exception in performSearch()'
			self.search_status = sys.exc_info()[0]
			print self.search_status
			return self.boat_list

		resTree = html.fromstring(res.content)

		boat_name = resTree.xpath('//table[@data-load="zebra"]//tr/td/a/text()')
		boat_vrn = resTree.xpath('//table[@data-load="zebra"]//tr/td[2]/text()')
		boat_oal = resTree.xpath('//table[@data-load="zebra"]//tr/td[3]/text()')
		boat_owner = resTree.xpath('//table[@data-load="zebra"]//tr/td[4]/text()')
		boat_link = resTree.xpath('//table[@data-load="zebra"]//tr/td/a/@href')

		iMax = len(boat_name)
		if iMax > 0:
			for i in range(iMax):
				the_boat = Boat(boat_vrn[i], boat_name[i], boat_oal[i], boat_owner[i])
				self.getExtraBoatInfo(the_boat, boat_link[i])
				self.boat_list.append(the_boat)
		return self.boat_list

	def getExtraBoatInfo(self, b, link):
		url = BoatList.base_url + link
		res = requests.get(url, headers=BoatList.headers)
		resTree = html.fromstring(res.content)

		extra_tree = resTree.xpath('//td[@align = "right"]')

		arrDOT = resTree.xpath('//td[contains(text(), "DOT")]/following-sibling::td/b/text()')
		arrSurveyed = resTree.xpath('//td[contains(text(), "Official Survey")]/following-sibling::td/b/text()')
		arrSurveyDate = resTree.xpath('//td[contains(text(), "Survey Date")]/following-sibling::td/b/text()')
		if len(arrDOT) > 0:
			b.dot = arrDOT[0]
			b.surveyed = arrSurveyed[0]
			if arrSurveyed[0] == 'Y':
				b.survey_date = arrSurveyDate[0]
			else:
				b.survey_date = ''

		arrTitles = resTree.xpath('//table[@data-load = "zebra"]/thead//tr/th')

		indexLic = -1
		indexArea = -1
		indexStatus = -1
		indexMVL = -1
		indexQuota = -1

		for i in range(len(arrTitles)):
			txtHeader = arrTitles[i].xpath('./text()')
			if txtHeader[0].find("Licence") >= 0:
				indexLic = i
			elif txtHeader[0].find("Area") >= 0:
				indexArea = i
			elif txtHeader[0].find("Status") >= 0:
				indexStatus = i
			elif txtHeader[0].find("MVL") >= 0:
				indexMVL = i
			elif txtHeader[0].find("Quota") >= 0:
				indexQuota = i

		arrLicRows = resTree.xpath('//table[@data-load = "zebra"]/tr')
		iMax = len(arrLicRows)
		txtLic = ''
		txtArea = ''
		txtStatus = ''
		txtMVL = ''
		txtQuota = ''
		if iMax > 0:
			for i in range(iMax):
				if indexLic >= 0:
					txtLic = arrLicRows[i].xpath('./td['+str(indexLic+1)+']/text()')
					if len(txtLic) > 0:
						txtLic = txtLic[0].strip()
				if indexArea >= 0:
					txtArea = arrLicRows[i].xpath('./td['+str(indexArea+1)+']/b/text()')
					if len(txtArea) > 0:
						txtArea = txtArea[0].strip()
				if indexStatus >= 0:
					txtStatus = arrLicRows[i].xpath('./td['+str(indexStatus+1)+']/text()')
					if len(txtStatus) > 0:
						txtStatus = txtStatus[0].strip()
				if indexMVL >= 0:
					txtMVL = arrLicRows[i].xpath('./td['+str(indexMVL+1)+']/text()')
					if len(txtMVL) > 0:
						txtMVL = txtMVL[0].strip()
				if indexQuota >= 0:
					txtQuota = arrLicRows[i].xpath('./td['+str(indexQuota+1)+']/text()')
					if len(txtQuota) > 0:
						txtQuota = txtQuota[0].strip()
				l = License(txtLic, txtArea, txtStatus, txtMVL, txtQuota)
				b.licenses.append(l)
					

class Boat:
	'Holds the data for a single boat'

	def __init__(self, vrn, name, oal, owner):
		self.vrn = str(vrn).strip()
		self.name = str(name).strip()
		self.overall_length = str(oal).strip()
		self.owner = str(owner).strip()
		self.dot = ''
		self.surveyed = ''
		self.survey_date = ''
		self.licenses = []

class License:
	'Holds data for a boat license'

	def __init__(self, lic_type, area, status, mvl='', quota=''):
		self.license_type = lic_type
		self.area = area
		self.status = status
		self.mvl = mvl
		self.quota = quota

#*************************************
#***** Console Interface code ********
#*************************************

def main():
	# vrn_input = raw_input('Enter VRN: ')
	# if not vrn_input.isdigit():
	# 	print 'VRN must be a number.'
	# 	main()

	# boats = BoatList(vrn_input)
	# #boats = BoatList('3092', 'Fan')
	# #boat_list = boats.searchByName()
	# boat_list = boats.searchByVRN()

	try:
		user_input = raw_input('Enter VRN or Vessel Name: ').upper()
	except:
		print '\n'
		return

	if not user_input.isdigit():
		boats = BoatList(search_name=user_input)
		boat_list = boats.searchByName()
	else:
		boats = BoatList(user_input)
		boat_list = boats.searchByVRN()

	if len(boat_list) > 0:
		print '\nSearch results\n--------------\n'
		for boat in boat_list:
			print 'Name:\t\t', boat.name
			print ' VRN:\t\t', boat.vrn
			print ' Length:\t', boat.overall_length
			print ' Owner:\t\t', boat.owner
			print ' DOT:\t\t', boat.dot
			print ' Surveyed:\t', boat.surveyed
			print ' Survey Date:\t', boat.survey_date
			if len(boat.licenses) > 0:
				if len(boat.licenses) > 1:
					print ' Licenses:'
				else:
					print ' License:'

				for l in boat.licenses:
					print '\tType:\t\t', l.license_type
					print '\tArea:\t\t', l.area
					print '\tStatus:\t\t', l.status
					print '\tMVL (m):\t', l.mvl
					print '\tQuota:\t\t', l.quota		
					if len(boat.licenses) > 1:
						print '\t------------'
			else:
				print ' * No current licences * '
			print ' ----------- '
	else:
		print 'No boat found for search [' + user_input + '].\n'
	main()

main()