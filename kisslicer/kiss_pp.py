#	Hier Accel anpassen bitte

accels = {
	'Top layer': 2000 ,			#	Accell der oberen Objektdecke

	'Perimeter Path': 2000 ,	#	Aussenwand und loop 1
	'Loop Path': 3000 ,			#	loop 2 bis loop n
	
	'Infill Path': 6000 ,		#	sparse infill - das mit den Prozenten
	'Solid Path': 6000 , 		#	Solides infill - Die richtigen "decken" und "böden"
	
	'Travel Path': 6000 ,		#	betrifft beides den Eilgang
	'Destring Suck': 6000 ,

	'Crown Path': 3000			#	Dünne Wände zum füllen von lücken
}

#	set your extrusion multiplers here

extrusion ={
	'Perimeter Path': 1 ,		#	Aussenwand und loop 1
	'Loop Path': 1.04 ,			#	loop 2 bis loop n
	
	'Infill Path': 1 ,			#	sparse infill - das mit den Prozenten
	'Solid Path': 1 , 			#	Solides infill - Die richtigen "decken" und "böden"

	'Crown Path': 1.08			#	Dünne Wände zum füllen von lücken
}

############################################################################
############################################################################

import sys, time

#
src_file = sys.argv[1]
#
try:
	gcode = []
	with open( src_file , 'r' ) as fp:  
		for cnt, line in enumerate(fp):
			gcode.append( line )
except Exception as e:
	raise e
	time.sleep(20)

top_on = [ 'TopLoop', 'TopPerimeter', 'TopSolid' ]
top_off = [ 'Prepare for End-Of-Layer', 'Prepare for Perimeter' ]
toplayer = False
allkeys = accels.keys()
extr_mult = 1
output = []
mean = []

for l in gcode:

	#	find extrusion typus
	if any(x in l for x in allkeys):
		h = [ key for key in allkeys if key in l ][0]
		accel_target = accels[h]
		mean.append(accels[h])
		extr_mult = extrusion.get(h, 1)

	#	trigger toplayer on
	if any(x in l for x in top_on):
		toplayer = True
		#output.append('; \t\t\t\t\t\t\t\t\t\t\t\t\t\t toplayer_toggle: ' + str(toplayer) + '\n')
	#	trigger toplayer off
	if any(x in l for x in top_off):
		toplayer = False
		#output.append('; \t\t\t\t\t\t\t\t\t\t\t\t\t\t toplayer_toggle: ' + str(toplayer) + '\n')
	#	overwrite accel if this is toplayer
	if toplayer and h != 'Destring Suck':
		#output.append('; toplayer_state: ' + str(toplayer) + '\n')
		accel_target = min( accel_target, accels['Top layer'] )
	#	apply accel
	if l.startswith( '; head speed' ):
		output.append( 'SET_VELOCITY_LIMIT ACCEL=' + str(accel_target) + ' ACCEL_TO_DECEL=' + str(accel_target) + ' SQUARE_CORNER_VELOCITY=5\n' )
	#	apply extrusion
	if l.startswith( 'G1 X' ) and extr_mult != 1:
		if extr_mult != 1:
			items = l.split(' ')
			for i in range(0,len(items)):
				if items[i].startswith('E'):
					items[i] = 'E' + str( round( float( items[i][1:] ) * extr_mult, 6 ))
			l = ' '.join(items) + '\n' # l + ' ; change:' + ' '.join(items) + '\n'

	output.append(l)

output.append( ';\t' + str(sum(mean) / len(mean)) )

with open( sys.argv[1] , 'w') as f:
	for line in output:
		f.write(line)

#	works with dwc2
#if sys.argv[2]:
#	import requests
#	url = 'http://192.168.10.130:4750/rr_upload'
#	with open( sys.argv[1] , 'rb' ) as f:
#		r = requests.post(url, name=sys.argv[2], data={'pxeconfig': f.read()})