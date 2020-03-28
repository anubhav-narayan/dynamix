'''
	DynaMIX Stereo
	Dynamic Multiple Instance Gain and Relative Loudness Analysis Stereo
	To achieve Diffused Sound Field over Stereo
'''
from pydub import AudioSegment
from pydub.scipy_effects import low_pass_filter
from pydub.scipy_effects import high_pass_filter
from pydub.scipy_effects import band_pass_filter
from pydub.playback import play
import numpy as np
import array
import sys
from pydub.utils import make_chunks
file_hanler=sys.argv[1].split('.')
print('Importing File',end='...')
sound = AudioSegment.from_file(sys.argv[1], format=file_hanler[-1])
print('Done')
def limiter(seg,limit_dB=-3,ratio=1):
	if seg.dBFS>limit_dB:
		seg=seg+((seg.dBFS-limit_dB)*ratio)
		pass
	return seg
	pass
def peak_limiter(seg,limit_dB=-0.3,ratio=1):
	if seg.dBFS>limit_dB:
		seg=seg+((seg.max_dBFS-limit_dB)*ratio)
		pass
	return seg
	pass
def to_ms(channel):
	'''
	Left-Right -> Mid-Side
	'''
	return [channel[0].overlay(channel[1]),channel[0].overlay(channel[1].invert_phase())]
	pass
def to_lr(channel):
	'''
	Mid-Side -> Left-Right
	'''
	return [channel[0].overlay(channel[1])-3,channel[0].overlay(channel[1].invert_phase())-3]
	pass
def dynamix_nr(channel,chunk_size=2,threshold=-40,gain_dB=15):
	'''
	DynaMIX Type I NR based on dbx Type II NR
	'''
	left_chunk=make_chunks(channel[0],chunk_size)
	right_chunk=make_chunks(channel[1],chunk_size)
	ret_channel=[AudioSegment.silent(duration=0,frame_rate=sound.frame_rate)]*2
	for x in range(0,len(left_chunk)):
		if left_chunk[x].dBFS<=threshold*3:
			left_chunk[x]=cheap_eq(left_chunk[x],6000,bandwidth=4000,gain_dB=gain_dB*3,order=2)
			left_chunk[x]=cheap_eq(left_chunk[x],8000,mode="high_shelf",gain_dB=-0.3,order=2)
			pass
		elif left_chunk[x].dBFS<=threshold*2:
			left_chunk[x]=cheap_eq(left_chunk[x],6000,bandwidth=4000,gain_dB=gain_dB*2,order=2)
			pass
		elif left_chunk[x].dBFS<=threshold:
			left_chunk[x]=cheap_eq(left_chunk[x],6000,bandwidth=4000,gain_dB=gain_dB,order=2)
			pass
		elif left_chunk[x].dBFS>threshold+30:
			left_chunk[x]=cheap_eq(left_chunk[x],6000,bandwidth=4000,gain_dB=-(left_chunk[x].dBFS-threshold+30),order=2)
			left_chunk[x]=cheap_eq(left_chunk[x],8000,mode="high_shelf",gain_dB=0.3,order=2)
			pass
		if right_chunk[x].dBFS<=threshold*3:
			right_chunk[x]=cheap_eq(right_chunk[x],6000,bandwidth=4000,gain_dB=gain_dB*3,order=2)
			right_chunk[x]=cheap_eq(right_chunk[x],8000,mode="high_shelf",gain_dB=-0.3,order=2)
			pass
		elif right_chunk[x].dBFS<=threshold*2:
			right_chunk[x]=cheap_eq(right_chunk[x],6000,bandwidth=4000,gain_dB=gain_dB*2,order=2)
			pass
		elif right_chunk[x].dBFS<=threshold:
			right_chunk[x]=cheap_eq(right_chunk[x],6000,bandwidth=4000,gain_dB=gain_dB,order=2)
			pass
		elif right_chunk[x].dBFS>threshold+30:
			right_chunk[x]=cheap_eq(right_chunk[x],6000,bandwidth=4000,gain_dB=-(right_chunk[x].dBFS-threshold+30),order=2)
			right_chunk[x]=cheap_eq(right_chunk[x],8000,mode="high_shelf",gain_dB=0.3,order=2)
			pass
		ret_channel[0]=ret_channel[0]+left_chunk[x]
		ret_channel[1]=ret_channel[1]+right_chunk[x]
		pass
	return ret_channel
	pass
def dynamix_nr_2(channel,chunk_size=0.6,threshold=-40,gain_dB=10):
	'''
	DynaMIX Type II NR based on dbx Type II NR
	'''
	channel=to_ms(channel)
	mid_chunk=make_chunks(channel[0],chunk_size)
	side_chunk=make_chunks(channel[1],chunk_size)
	ret_channel=[AudioSegment.silent(duration=0,frame_rate=sound.frame_rate)]*2
	for x in range(0,len(mid_chunk)):
		if side_chunk[x].dBFS<=threshold*3:
			side_chunk[x]=cheap_eq(side_chunk[x],6000,bandwidth=4000,gain_dB=gain_dB*3,order=2)
			side_chunk[x]=cheap_eq(side_chunk[x],8000,mode="high_shelf",gain_dB=-0.3,order=2)
			pass
		elif side_chunk[x].dBFS<=threshold*2:
			side_chunk[x]=cheap_eq(side_chunk[x],6000,bandwidth=4000,gain_dB=gain_dB*2,order=2)
			pass
		elif side_chunk[x].dBFS<=threshold:
			side_chunk[x]=cheap_eq(side_chunk[x],6000,bandwidth=4000,gain_dB=gain_dB,order=2)
			pass
		elif side_chunk[x].dBFS>threshold+30:
			side_chunk[x]=cheap_eq(side_chunk[x],6000,bandwidth=4000,gain_dB=abs(side_chunk[x].dBFS-threshold-30),order=2)
			side_chunk[x]=cheap_eq(side_chunk[x],8000,mode="high_shelf",gain_dB=0.3,order=2)
			pass
		if mid_chunk[x].dBFS<=threshold*3:
			mid_chunk[x]=cheap_eq(mid_chunk[x],9000,bandwidth=6000,gain_dB=gain_dB/6,order=2)
			mid_chunk[x]=cheap_eq(mid_chunk[x],12000,mode="high_shelf",gain_dB=0.3,order=2)
			pass
		elif mid_chunk[x].dBFS<=threshold*2:
			mid_chunk[x]=cheap_eq(mid_chunk[x],9000,bandwidth=6000,gain_dB=gain_dB/4,order=2)
			pass
		elif mid_chunk[x].dBFS<=threshold:
			mid_chunk[x]=cheap_eq(mid_chunk[x],9000,bandwidth=6000,gain_dB=gain_dB/2,order=2)
			pass
		elif mid_chunk[x].dBFS>threshold+30:
			mid_chunk[x]=cheap_eq(mid_chunk[x],9000,bandwidth=6000,gain_dB=-abs(side_chunk[x].dBFS-threshold-30),order=2)
			mid_chunk[x]=cheap_eq(mid_chunk[x],12000,mode="high_shelf",gain_dB=-0.3,order=2)
			pass
		ret_channel[0]=ret_channel[0]+mid_chunk[x]
		ret_channel[1]=ret_channel[1]+side_chunk[x]
		pass
	ret_channel=to_lr(ret_channel)
	return [peak_limiter(ret_channel[0],ratio=2),peak_limiter(ret_channel[1],ratio=2)]
	pass
def dynamix_side_level(channel,chunk_size=10):
	'''
	Mid Leveled Side Extraction for better Separation of Side Channel
	'''
	l_chunk=make_chunks(channel[0],chunk_size)
	r_chunk=make_chunks(channel[1],chunk_size)
	ret_channel=[AudioSegment.silent(duration=0,frame_rate=sound.frame_rate)]*2
	for x in range(0,len(l_chunk)):
		if l_chunk[x].dBFS>r_chunk[x].dBFS:
			l_chunk[x]=l_chunk[x]-(r_chunk[x].dBFS-l_chunk[x].dBFS)
			pass
		if r_chunk[x].dBFS>l_chunk[x].dBFS:
			r_chunk[x]=r_chunk[x]-(l_chunk[x].dBFS-r_chunk[x].dBFS)
			pass
		ret_channel[0]=ret_channel[0]+l_chunk[x]
		ret_channel[1]=ret_channel[1]+r_chunk[x]
		pass
	return [ret_channel[0].overlay(ret_channel[1].invert_phase(),position=0),ret_channel[1].overlay(ret_channel[0].invert_phase(),position=0)]
	pass
def dynamix_mid_level(channel,chunk_size=10):
	'''
	Side Leveled Mid Extraction for better Separation of Mid Channel
	'''
	l_chunk=make_chunks(channel[0],chunk_size)
	r_chunk=make_chunks(channel[1],chunk_size)
	ret_channel=[AudioSegment.silent(duration=0,frame_rate=sound.frame_rate)]*2
	for x in range(0,len(l_chunk)):
		if l_chunk[x].dBFS>r_chunk[x].dBFS:
			l_chunk[x]=l_chunk[x]-(r_chunk[x].dBFS-l_chunk[x].dBFS)
			pass
		if r_chunk[x].dBFS>l_chunk[x].dBFS:
			r_chunk[x]=r_chunk[x]-(l_chunk[x].dBFS-r_chunk[x].dBFS)
			pass
		ret_channel[0]=ret_channel[0]+l_chunk[x]
		ret_channel[1]=ret_channel[1]+r_chunk[x]
		pass
	return ret_channel[0].overlay(ret_channel[1])
	pass
def dynamix_particle(channel):
	return [channel[0].overlay((channel[1]-9.5).invert_phase(),position=0.25),channel[1].overlay((channel[0]-9.5).invert_phase(),position=0.25),channel[0].overlay((channel[1]-11.5).invert_phase(),position=0.4999),channel[1].overlay((channel[0]-11.5).invert_phase(),position=0.4999),channel[0].overlay((channel[1]-12).invert_phase(),position=0.6874),channel[1].overlay((channel[0]-12).invert_phase(),position=0.6874)]
	pass	
def cheap_eq(seg,focus_freq,bandwidth=100,mode="peak",gain_dB=0,order=2):
	'''
	Cheap EQ in PyDub
	Silence=-120dBFS
	I2/I1=2=>3dB SPL Gain
	'''
	if gain_dB>=0:
		if mode=="peak":
			sec=band_pass_filter(seg,focus_freq-bandwidth/2,focus_freq+bandwidth/2,order=order)
			seg=seg.overlay(sec-(3-gain_dB))
			return peak_limiter(seg)
			pass
		if mode=="low_shelf":
			sec=low_pass_filter(seg,focus_freq,order=order)
			seg=seg.overlay(sec-(3-gain_dB))
			return peak_limiter(seg)
			pass
		if mode=="high_shelf":
			sec=high_pass_filter(seg,focus_freq,order=order)
			seg=seg.overlay(sec-(3-gain_dB))
			return peak_limiter(seg)
			pass
		pass
	if gain_dB<0:
		if mode=="peak":
			sec=high_pass_filter(seg,focus_freq-bandwidth/2,order=order)
			seg=seg.overlay(sec-(3+gain_dB))+gain_dB
			sec=low_pass_filter(seg,focus_freq+bandwidth/2,order=order)
			seg=seg.overlay(sec-(3+gain_dB))+gain_dB
			return peak_limiter(seg)
			pass
		if mode=="low_shelf":
			sec=high_pass_filter(seg,focus_freq,order=order)
			seg=seg.overlay(sec-(3+gain_dB))+gain_dB
			return peak_limiter(seg)
			pass
		if mode=="high_shelf":
			sec=low_pass_filter(seg,focus_freq,order=order)
			seg=seg.overlay(sec-(3+gain_dB))+gain_dB
			return peak_limiter(seg)
			pass
		pass
	pass
'''
Split Left and Right Channels
'''
print('Spliting Channels',end='...')
channel=(sound).split_to_mono()
channel=dynamix_nr_2(channel)
channel=dynamix_nr(channel,chunk_size=2,gain_dB=6)
# channel=[sound,sound]
'''
Create Mid Channel
Mid Channel = Left Channel + Right Channel
'''
mid_channel=dynamix_mid_level(channel)
'''
Ex Channels
'''
ex_channel=dynamix_particle(channel)
'''
Create Side Channels
Left Side Channel = Left Channel - Right Channel
Right Side Channel = Right Channel - Left Channel
'''
rear_channel=dynamix_side_level(channel)
rear_channel=dynamix_nr(rear_channel)
side_channel=dynamix_particle(rear_channel)
print('Done')
'''
Process to DynaMIX sample
PyDub Sample Time = 100ms
1 DynaMIX sample = 100*44.1 samples [at 44.1kHz]
				 = 100*48 samples [at 48kHz]
		 		 = 100*96 samples [at 96kHz]
'''
print('Processing DynaMIX Stereo')
print('\tTime Domain Processing')
'''
DynaMIX Sample Processing:-
Time Domain Gain Analysis: Using Relative Dominance
Relative Stereo Separation
'''
#Bass Band
mid_channel=cheap_eq(mid_channel,250,mode="low_shelf",gain_dB=6,order=2)
mid_channel=cheap_eq(mid_channel,650,mode="high_shelf",gain_dB=-24,order=2)
rear_channel[0]=high_pass_filter(rear_channel[0],100,order=2)
rear_channel[1]=high_pass_filter(rear_channel[1],100,order=2)
ex_channel[0]=cheap_eq(ex_channel[0],250,mode="low_shelf",gain_dB=1.5,order=2)
ex_channel[1]=cheap_eq(ex_channel[1],250,mode="low_shelf",gain_dB=1.5,order=2)
ex_channel[4]=cheap_eq(ex_channel[4],650,mode="low_shelf",gain_dB=-18,order=2)
ex_channel[5]=cheap_eq(ex_channel[5],650,mode="low_shelf",gain_dB=-18,order=2)
ex_channel[4]=cheap_eq(ex_channel[4],250,mode="low_shelf",gain_dB=0.3,order=2)
ex_channel[5]=cheap_eq(ex_channel[5],250,mode="low_shelf",gain_dB=0.3,order=2)
ex_channel[4]=cheap_eq(ex_channel[4],1000,mode="high_shelf",gain_dB=1.5,order=2)
ex_channel[5]=cheap_eq(ex_channel[5],1000,mode="high_shelf",gain_dB=1.5,order=2)
side_channel[0]=cheap_eq(side_channel[0],1000,bandwidth=0,gain_dB=6,order=2)
side_channel[1]=cheap_eq(side_channel[1],1000,bandwidth=0,gain_dB=6,order=2)
side_channel[2]=cheap_eq(side_channel[2],1000,bandwidth=0,gain_dB=6,order=2)
side_channel[3]=cheap_eq(side_channel[3],1000,bandwidth=0,gain_dB=6,order=2)
rear_channel[0]=cheap_eq(rear_channel[0],1000,bandwidth=0,gain_dB=9,order=2)
rear_channel[1]=cheap_eq(rear_channel[1],1000,bandwidth=0,gain_dB=9,order=2)
#Mid Band
mid_channel=cheap_eq(mid_channel,8000,bandwidth=6000,gain_dB=24,order=2)
mid_channel=cheap_eq(mid_channel,4507,bandwidth=1033,gain_dB=-3,order=2)
ex_channel[0]=cheap_eq(ex_channel[0],6000,bandwidth=4000,gain_dB=1.5,order=2)
ex_channel[0]=cheap_eq(ex_channel[0],4507,bandwidth=1033,gain_dB=-3,order=2)
ex_channel[1]=cheap_eq(ex_channel[1],6000,bandwidth=4000,gain_dB=1.5,order=2)
ex_channel[1]=cheap_eq(ex_channel[1],4507,bandwidth=1033,gain_dB=-3,order=2)
ex_channel[2]=cheap_eq(ex_channel[2],4507,bandwidth=1033,gain_dB=-0.75,order=2)
ex_channel[3]=cheap_eq(ex_channel[3],4507,bandwidth=1033,gain_dB=-0.75,order=2)
ex_channel[4]=cheap_eq(ex_channel[4],8000,bandwidth=6000,gain_dB=-6,order=2)
ex_channel[5]=cheap_eq(ex_channel[5],8000,bandwidth=6000,gain_dB=-6,order=2)
ex_channel[4]=cheap_eq(ex_channel[4],4507,bandwidth=1033,gain_dB=-6,order=2)
ex_channel[5]=cheap_eq(ex_channel[5],4507,bandwidth=1033,gain_dB=-6,order=2)
side_channel[4]=cheap_eq(side_channel[4],8000,bandwidth=6000,gain_dB=-6,order=2)
side_channel[5]=cheap_eq(side_channel[5],8000,bandwidth=6000,gain_dB=-6,order=2)
side_channel[2]=cheap_eq(side_channel[2],4507,bandwidth=1033,gain_dB=0.75,order=2)
side_channel[3]=cheap_eq(side_channel[3],4507,bandwidth=1033,gain_dB=0.75,order=2)
side_channel[0]=cheap_eq(side_channel[0],4507,bandwidth=1033,gain_dB=-1.5,order=2)
side_channel[1]=cheap_eq(side_channel[1],4507,bandwidth=1033,gain_dB=-1.5,order=2)
rear_channel[0]=cheap_eq(rear_channel[0],6000,bandwidth=4000,gain_dB=6,order=2)
rear_channel[1]=cheap_eq(rear_channel[1],6000,bandwidth=4000,gain_dB=6,order=2)
rear_channel[0]=cheap_eq(rear_channel[0],4507,bandwidth=1033,gain_dB=3,order=2)
rear_channel[1]=cheap_eq(rear_channel[1],4507,bandwidth=1033,gain_dB=3,order=2)
#High Band
ex_channel[2]=cheap_eq(ex_channel[2],8993,mode="high_shelf",gain_dB=3,order=2)
ex_channel[3]=cheap_eq(ex_channel[3],8993,mode="high_shelf",gain_dB=3,order=2)
ex_channel[4]=cheap_eq(ex_channel[4],11314,mode="high_shelf",gain_dB=0.5,order=2)
ex_channel[5]=cheap_eq(ex_channel[5],11314,mode="high_shelf",gain_dB=0.5,order=2)
side_channel[0]=cheap_eq(side_channel[0],8993,mode="high_shelf",gain_dB=-18,order=2)
side_channel[1]=cheap_eq(side_channel[1],8993,mode="high_shelf",gain_dB=-18,order=2)
side_channel[0]=cheap_eq(side_channel[0],14253,mode="high_shelf",gain_dB=15,order=2)
side_channel[1]=cheap_eq(side_channel[1],14253,mode="high_shelf",gain_dB=15,order=2)
side_channel[2]=cheap_eq(side_channel[2],8993,mode="high_shelf",gain_dB=-18,order=2)
side_channel[3]=cheap_eq(side_channel[3],8993,mode="high_shelf",gain_dB=-18,order=2)
side_channel[2]=cheap_eq(side_channel[2],17943,mode="high_shelf",gain_dB=12,order=2)
side_channel[3]=cheap_eq(side_channel[3],17943,mode="high_shelf",gain_dB=12,order=2)
side_channel[4]=cheap_eq(side_channel[4],8993,mode="high_shelf",gain_dB=-18,order=2)
side_channel[5]=cheap_eq(side_channel[5],8993,mode="high_shelf",gain_dB=-18,order=2)
side_channel[4]=cheap_eq(side_channel[4],11314,mode="high_shelf",gain_dB=15,order=2)
side_channel[5]=cheap_eq(side_channel[5],11314,mode="high_shelf",gain_dB=15,order=2)
rear_channel[0]=low_pass_filter(rear_channel[0],7592,order=2)
rear_channel[1]=low_pass_filter(rear_channel[1],7592,order=2)
#Combination
reflect_level=-6
f_amb_fact=[(0.08575/0.343),(0.1/0.343)]
s_amb_fact=(np.sqrt(4**2+4**2)/0.343)
r_amb_fact=30+(np.sqrt(2**2+7**2)/0.343)
channel[0]=(mid_channel-5.75)
channel[0]=channel[0].overlay(ex_channel[0]-12.5,position=f_amb_fact[0])
channel[0]=channel[0].overlay(ex_channel[2]-9.5,position=f_amb_fact[1])
channel[0]=channel[0].overlay(ex_channel[4],position=s_amb_fact+0.6874)
channel[0]=channel[0].overlay(side_channel[4]+reflect_level,position=30+s_amb_fact+0.6874)
channel[0]=channel[0].overlay(side_channel[2]-9.5+reflect_level,position=r_amb_fact+0.8749)
channel[0]=channel[0].overlay(side_channel[0]-12.5+reflect_level,position=r_amb_fact+1.2082)
channel[0]=channel[0].overlay(rear_channel[0]-5.75+reflect_level,position=r_amb_fact+1.3748)
channel[1]=(mid_channel-5.75)
channel[1]=channel[1].overlay(ex_channel[1]-12.5,position=f_amb_fact[0])
channel[1]=channel[1].overlay(ex_channel[2]-9.5,position=f_amb_fact[1])
channel[1]=channel[1].overlay(ex_channel[5],position=s_amb_fact+0.6874)
channel[1]=channel[1].overlay(side_channel[5]+reflect_level,position=20+s_amb_fact+0.6874)
channel[1]=channel[1].overlay(side_channel[3]-9.5+reflect_level,position=r_amb_fact+0.8749)
channel[1]=channel[1].overlay(side_channel[1]-12.5+reflect_level,position=r_amb_fact+1.2082)
channel[1]=channel[1].overlay(rear_channel[1]-5.75+reflect_level,position=r_amb_fact+1.3748)
channel=dynamix_nr_2(channel)
sound_final=AudioSegment.from_mono_audiosegments(peak_limiter(channel[0]),peak_limiter(channel[1]))
sound_final.export("DynaMIX(48kHz).irs",format="wav")
