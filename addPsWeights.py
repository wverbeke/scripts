import sys
sys.path.append('/afs/cern.ch/cms/PPD/PdmV/tools/McM/')
from rest import McM

mcm = McM(dev=False)

requests_to_update = list('SUS-RunIIFall18wmLHEGS-000' + str(i) for i in range(99,100) )

for request_id in requests_to_update:
    
    request = mcm.get('requests', request_id)
    print( request_id )
    
    request['fragment'] = request['fragment'].replace( 'pythia8CP5SettingsBlock,', 'pythia8CP5SettingsBlock, pythia8PSweightsSettingsBlock,' )
    request['fragment'] = request['fragment'].replace( "'pythia8CP5Settings',", "'pythia8CP5Settings', 'pythia8PSweightsSettings', " )
    request['fragment'] = request['fragment'].replace( 'from Configuration.Generator.MCTunes2017.PythiaCP5Settings_cfi import *', 'from Configuration.Generator.MCTunes2017.PythiaCP5Settings_cfi import *\nfrom Configuration.Generator.PSweightsPythia.PythiaPSweightsSettings_cfi import *')
    
    update_response = mcm.update('requests', request)

