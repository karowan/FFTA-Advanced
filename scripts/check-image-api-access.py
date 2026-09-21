"""Read-only Gemini model discovery; no generation or paid inference."""
import datetime, json, urllib.request, urllib.error
from image_api_credentials import ROOT, read_key

key=read_key('GEMINI_API_KEY')
request=urllib.request.Request('https://generativelanguage.googleapis.com/v1beta/models',headers={'x-goog-api-key':key})
out=ROOT/'build/art/provider-comparison'
out.mkdir(parents=True,exist_ok=True)
try:
    with urllib.request.urlopen(request,timeout=30) as response:
        data=json.load(response)
    models=[{'name':m['name'],'displayName':m.get('displayName'),'methods':m.get('supportedGenerationMethods',[])} for m in data.get('models',[]) if any(v in m['name'].lower() for v in ('image','imagen'))]
    report={'status':'authenticated','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'provider':'Google Gemini','operation':'GET model catalog only; no image generation','imageModels':models}
    (out/'gemini-access.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))
except urllib.error.HTTPError as error:
    report={'status':'failed','httpStatus':error.code,'provider':'Google Gemini','operation':'GET model catalog only'}
    (out/'gemini-access.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report)); raise SystemExit(1)
