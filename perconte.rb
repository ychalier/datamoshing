# ffmpeg : to prores 422
# DONNÉES

# video

wi = 3840
he = 2160
co = 1.5
 # coefficient

wi = wi * co
he = he * co

scal = "neighbor" #sacle algo bilinear neighbor
meth = "zero" #-me_method umh

# compression

br = "211277"
ii = "20"  #keyframes 1 - 100

#files

ext = "is#{co}K"

# DONNÉES

a = ARGV[0]
aname = a.split(".")
o = "#{aname[0]}_#{ext}_@#{br}k_M#{meth}_i#{ii}.avi"

puts "#{a} -> #{o}"

# FF SHELL

reverse = "" #",reverse"

value = %x( echo 'ffmpeg -y -i "#{a}" -vf scale=#{wi}:#{he}:flags=#{scal}#{reverse} -c:v libxvid -b:v #{br}k -sc_threshold 0 -g #{ii} -me_method #{meth} -c:a libmp3lame -b:a 256k "#{o}"' )
value = %x[ #{value} ]

# -vf scale=3840:2160:flags=#{scal}

# ffplay -flags2 +export_mvs -i AVAFALL33_is1K_@222557k_Mumph_199999_ffo.avi -vf codecview=mv=pf+bf+bb