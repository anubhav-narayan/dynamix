'''
	DynaMIX Stereo
	Dynamic Multiple Instance Gain and Relative Loudness Analysis Stereo
	To achieve Diffused Sound Field over Stereo
'''
from pydub import AudioSegment
from pydub.scipy_effects import low_pass_filter
from pydub.scipy_effects import high_pass_filter
from pydub.playback import play
from scipy.fftpack import fft
import numpy as np
import array
import sys
from pydub.utils import make_chunks
file_hanler=sys.argv[1].split('.')
print('Importing File',end='...')
sound = AudioSegment.from_file(sys.argv[1], format=file_hanler[-1])
sound.set_frame_rate(48000)
print('Done')
def stereo_sepration(dB_sepration,seg):
	'''
	Stereo Separation in Decibels
	'''
	channel=seg.split_to_mono()
	channel[0]=channel[0].overlay((channel[1]-dB_sepration).invert_phase())
	channel[1]=channel[1].overlay((channel[0]-dB_sepration).invert_phase())
	seg=AudioSegment.from_mono_audiosegments(channel[0],channel[1])
	return seg
def stereo_sepration_from_mono(dB_sepration,seg_left,seg_right):
	'''
	Stereo Separation in Decibels
	'''
	channel=[seg_left,seg_right]
	channel[0]=channel[0].overlay((channel[1]-dB_sepration).invert_phase())
	channel[1]=channel[1].overlay((channel[0]-dB_sepration).invert_phase())
	seg=[channel[0],channel[1]]
	return seg
def stereo_sepration_list(dB_sepration,channel):
	'''
	Stereo Separation in Decibels
	'''
	channel[0]=channel[0].overlay((channel[1]-dB_sepration).invert_phase())
	channel[1]=channel[1].overlay((channel[0]-dB_sepration).invert_phase())
	seg=[channel[0],channel[1]]
	return seg
def range_level(seg,target_dB,threshold):
	'''
	Leveler
	'''
	if (seg.dBFS-target_dB)<-threshold:
		seg=seg+(seg.dBFS-target_dB)-threshold
		pass
	elif (seg.dBFS-target_dB)>threshold:
		seg=seg+(seg.dBFS-target_dB)+threshold
		pass
	return seg
def flat_level(seg,target_dB):
	'''
	Leveler
	'''
	seg=seg+(seg.max_dBFS-target_dB)
	return seg
def top_limiter(seg,top_dB=-20):
	'''
	Limiter
	'''
	if seg.max_dBFS>top_dB:
		seg=seg-(seg.max_dBFS-top_dB)
		pass
	return seg
def soft_top_limiter(seg,top_dB=-20):
	'''
	Limiter
	'''
	if seg.dBFS>top_dB:
		seg=seg-(seg.dBFS-top_dB)
		pass
	return seg
def base_expander(seg,base_dB=-96):
	'''
	Delimiter
	'''
	if seg.max_dBFS<base_dB:
		seg=seg+(base_dB-seg.max_dBFS)
		pass
	return seg
'''
Split Left and Right Channels
'''
print('Spliting Channels',end='...')
channel=sound.split_to_mono()
'''
Create Mid Channel
Mid Channel = Left Channel + Right Channel
'''
mid_channel=channel[0].overlay(channel[1])
'''
Create Side Channels
Left Side Channel = Left Channel - Right Channel
Right Side Channel = Right Channel - Left Channel
'''
side_channel=[channel[0].overlay(channel[1].invert_phase()),channel[1].overlay(channel[0].invert_phase())]
side_channel=stereo_sepration_list(6,side_channel)
print('Done')
'''
Process to DynaMIX sample
1 DynaMIX sample = 256*44.1 samples [at 44.1kHz]
				 = 256*48 samples [at 48kHz]
		 		 = 256*96 samples [at 96kHz]
'''
print('Processing DynaMIX Stereo')
left_chunk=make_chunks(channel[0],256)
right_chunk=make_chunks(channel[1],256)
mid_chunk=make_chunks(mid_channel,256)
side_left_chunk=make_chunks(side_channel[0],256)
side_right_chunk=make_chunks(side_channel[1],256)
'''
TODO
DynaMIX Sample Processing:-
Frequency Domain Gain Analysis
'''
print('\tTime Domain Processing',end='...')
'''
DynaMIX Sample Processing:-
Time Domain Gain Analysis: Using Relative Dominance
Relative Stereo Separation
'''
#Channel Processing
for x in range(0,len(left_chunk)):
	l=left_chunk[x].max_dBFS
	r=right_chunk[x].max_dBFS
	m=mid_chunk[x].max_dBFS
	sl=side_left_chunk[x].max_dBFS
	sr=side_right_chunk[x].max_dBFS
	if m==l==r==sl==sr:
		side_left_chunk[x]=side_left_chunk[x]-6
		side_right_chunk[x]=side_right_chunk[x]-6
		low_pass_filter(side_right_chunk[x],7000,order=2)
		low_pass_filter(side_left_chunk[x],7000,order=2)
		mid_chunk[x]=mid_chunk[x]-3
		left_chunk[x]=stereo_sepration_from_mono(6,left_chunk[x],right_chunk[x])[0]
		right_chunk[x]=stereo_sepration_from_mono(6,left_chunk[x],right_chunk[x])[1]
		pass
	elif m==max(m,l,r,sl,sr):
		mid_chunk[x]=mid_chunk[x]-3
		side_left_chunk[x]=side_left_chunk[x]-6
		side_right_chunk[x]=side_right_chunk[x]-6
		left_chunk[x]=stereo_sepration_from_mono(3,left_chunk[x],right_chunk[x])[0]
		right_chunk[x]=stereo_sepration_from_mono(3,left_chunk[x],right_chunk[x])[1]
		pass
	elif sl==max(m,l,r,sl,sr) and sr==max(m,l,r,sl,sr):
		side_left_chunk[x]=side_left_chunk[x]-4.5
		side_right_chunk[x]=side_right_chunk[x]-4.5
		mid_chunk[x]=mid_chunk[x]-6
		left_chunk[x]=stereo_sepration_from_mono(4.5,left_chunk[x],right_chunk[x])[0]
		right_chunk[x]=stereo_sepration_from_mono(4.5,left_chunk[x],right_chunk[x])[1]
		pass
	elif sl==max(m,l,r,sl,sr):
		side_left_chunk[x]=side_left_chunk[x]-4.5
		side_right_chunk[x]=side_right_chunk[x]-6
		low_pass_filter(side_right_chunk[x],7000,order=2)
		mid_chunk[x]=mid_chunk[x]-3
		left_chunk[x]=stereo_sepration_from_mono(6,left_chunk[x],right_chunk[x])[0]
		right_chunk[x]=stereo_sepration_from_mono(9,left_chunk[x],right_chunk[x])[1]
		pass
	elif sr==max(m,l,r,sl,sr):
		side_left_chunk[x]=side_left_chunk[x]-6
		side_right_chunk[x]=side_right_chunk[x]-4.5
		low_pass_filter(side_left_chunk[x],7000,order=2)
		mid_chunk[x]=mid_chunk[x]-3
		left_chunk[x]=stereo_sepration_from_mono(9,left_chunk[x],right_chunk[x])[0]
		right_chunk[x]=stereo_sepration_from_mono(6,left_chunk[x],right_chunk[x])[1]
		pass
	elif l==max(m,l,r,sl,sr) and r==max(m,l,r,sl,sr):
		side_left_chunk[x]=side_left_chunk[x]-6
		side_right_chunk[x]=side_right_chunk[x]-6
		low_pass_filter(side_right_chunk[x],7000,order=3)
		low_pass_filter(side_left_chunk[x],7000,order=3)
		mid_chunk[x]=mid_chunk[x]-3
		left_chunk[x]=stereo_sepration_from_mono(10.5,left_chunk[x],right_chunk[x])[0]
		right_chunk[x]=stereo_sepration_from_mono(10.5,left_chunk[x],right_chunk[x])[1]
		pass
	elif l==max(m,l,r,sl,sr):
		side_left_chunk[x]=side_left_chunk[x]-6
		side_right_chunk[x]=side_right_chunk[x]-4.5
		low_pass_filter(side_right_chunk[x],7000,order=5)
		low_pass_filter(side_left_chunk[x],7000,order=2)
		mid_chunk[x]=mid_chunk[x]-3
		left_chunk[x]=stereo_sepration_from_mono(10.5,left_chunk[x],right_chunk[x])[0]
		right_chunk[x]=stereo_sepration_from_mono(9,left_chunk[x],right_chunk[x])[1]
		pass
	elif r==max(m,l,r,sl,sr):
		side_right_chunk[x]=side_right_chunk[x]-6
		side_left_chunk[x]=side_left_chunk[x]-4.5
		low_pass_filter(side_right_chunk[x],7000,order=2)
		low_pass_filter(side_left_chunk[x],7000,order=5)
		mid_chunk[x]=mid_chunk[x]-3
		left_chunk[x]=stereo_sepration_from_mono(9,left_chunk[x],right_chunk[x])[0]
		right_chunk[x]=stereo_sepration_from_mono(10.5,left_chunk[x],right_chunk[x])[1]
		pass
	'''
	Static Separation of Channels
	'''
	#left_chunk[x]=stereo_sepration_from_mono(60,left_chunk[x],mid_chunk[x])[0]
	#right_chunk[x]=stereo_sepration_from_mono(60,right_chunk[x],mid_chunk[x])[0]
	#side_left_chunk[x]=stereo_sepration_from_mono(60,side_left_chunk[x],left_chunk[x])[0]
	#side_right_chunk[x]=stereo_sepration_from_mono(60,side_right_chunk[x],right_chunk[x])[0]
	pass
print('Done')
'''
Recombination
Delay Key Frequency = 60Hz
Rear Delay = (1/DKF)*(1/2-1/6) = 13.8889ms for 120 degrees at 60Hz
'''
print('Recombining Channels',end='...')
channel_final=[AudioSegment.silent(duration=100,frame_rate=sound.frame_rate)]*5
for x in range(0,len(left_chunk)):
	'''
	Range Levelling
	Compression for Channels
	'''
	range_level(left_chunk[x],-60,6)
	range_level(right_chunk[x],-60,6)
	range_level(mid_chunk[x],-60,12)
	range_level(side_left_chunk[x],-72,6)
	range_level(side_right_chunk[x],-72,6)
	base_expander(mid_chunk[x])
	channel_final[0]=channel_final[0]+(left_chunk[x])
	channel_final[1]=channel_final[1]+(right_chunk[x])
	channel_final[2]=channel_final[2]+(mid_chunk[x])
	channel_final[3]=channel_final[3]+(side_left_chunk[x])
	channel_final[4]=channel_final[4]+(side_right_chunk[x])
	pass
channel_final[0]=channel_final[2].overlay(channel_final[0]).overlay(channel_final[3],position=13.8889)
#Master Limiter Left
channel_final[0]=top_limiter(channel_final[0],-9)
channel_final[1]=channel_final[2].overlay(channel_final[1]).overlay(channel_final[4],position=13.8889)
#Master Limiter Right
channel_final[1]=top_limiter(channel_final[1],-9)
sound_final=AudioSegment.from_mono_audiosegments(channel_final[0].normalize()-6,channel_final[1].normalize()-6).normalize().remove_dc_offset()
print('Done')
play(sound_final)