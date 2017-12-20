import os
import urllib
import boto3
from subprocess import Popen, PIPE
import library_location
# used to find and import the ffmpeg binary file
library_location.set_path_if_library_not_available('ffmpeg','lib','ffmpeg is required for this library, but was not found')

# set the path of where you want files to be saved (i.e. 'audio/mp3')
save_path = 'mp3Files'

s3 = boto3.client('s3')

def lambda_handler(event, context):
    # read bucket and key from event data
    record = event['Records'][0]['s3']
    bucket = record['bucket']['name']
    key = urllib.unquote_plus(record['object']['key'])

    # generate new key name with the save_path and same file name (i.e. audio/mp3/file.mp3)
    new_key = "%s/%s.mp3" % (save_path, os.path.basename(key).replace(".wav", ""))

    # read the wav file and store as bytes
    wav_audio = s3.get_object(Bucket=bucket, Key=key)['Body'].read()

    try:
        mp3_audio = audio_bytes_to_mp3_bytes(wav_audio)
    except Exception as e:
        print "EXCEPTION ---->"
        print e
        quit()

    # save new mp3 audio to s3
    s3.put_object(
        Body=mp3_audio,
        Key=new_key,
        Bucket=bucket,
    )

def audio_bytes_to_mp3_bytes(audio_bytes):
    ''' convert the wav audio bytes to mp3 audio bytes '''
    process = Popen('ffmpeg -i pipe:0 -f mp3 pipe:1'.split(), stdout=PIPE, stdin=PIPE)
    stdout, stderr = process.communicate(input = audio_bytes)
    return stdout