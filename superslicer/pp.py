
import sys, re, time

#############
#	accel, acceltodecel, squarecorner
travel = [ 4000, 4000, 5 ]

#############
output = []

target = travel
saved = [ 0, 0, 0 ]
last = [ 0,0,0 ]

untrigger = False

gcode = open(sys.argv[1], 'r')
content = gcode.read()

alltravels = re.findall('G1 X\d+.\d+ Y\d+.\d+ F(\d+.\d+?)', content)
alltravels.append('4711')
travelspeed = str(max([ float(x) for x in  alltravels ]))

extr_trigger = False
extr_mult = 1.0
more_extrusion = {
	';TYPE:Perimeter': 1.0 ,
	';TYPE:External perimeter': 1.0, #1.035,
	';TYPE:Gap fill': 1.0 ,

	';TYPE:Solid infill': 1.0 ,
	';TYPE:Internal infill': 1.0 ,
	';TYPE:Top solid infill': 1.0
}

try:
	with open( sys.argv[1] , 'r' ) as fp:  
		for cnt, line in enumerate(fp):

			#	pick existing accel
			if "SET_VELOCITY_LIMIT" in line:
				numbers = re.findall(r'\d+', line)
				target = last = saved = [ numbers[0] , numbers[1] , numbers[2] ]

			if travelspeed in line:
				target = travel
				untrigger = True

			if untrigger and re.match('G1 F\d+', line):
				target = saved
				untrigger = False

			if target != last:
				output.append("SET_VELOCITY_LIMIT ACCEL=" + str(target[0]) + " ACCEL_TO_DECEL=" + str(target[1]) + " SQUARE_CORNER_VELOCITY=" + str(target[2]) + "\n")
				last = target

			#	extrusiontype changes
			if ";TYPE:" in line:
				try:
					extr_mult = more_extrusion[line[:-1]]
				except Exception as e:
					extr_mult = 1.0

				if any(word in line for word in more_extrusion.keys()) and extr_mult != 1.0:
					extr_trigger = True
					line = line + "; extr_mult= " + str(extr_mult) + "\n"
				else:
					extr_trigger = False
					extr_mult = 1.0
					line = line + "; extr_mult= " + str(extr_mult) + "\n"

			if extr_trigger and "G1 X" in line and extr_mult != 1.0:
				items = line.split(' ')
				#orgline = line
				for i in range(0,len(items)):
					if items[i].startswith('E'):
						items[i] = 'E' + str( round( float( items[i][1:] ) * extr_mult, 6 ))
					line = ' '.join(items) + "\n"# + ' ; mult ' + str(extr_mult)
				#import pdb; pdb.set_trace()

			output.append(line)

except Exception as e:
	print(e)
	time.sleep(200)


#	overwrite original file
with open( sys.argv[1] , 'w') as f:
	for line in output:
		f.write(line)