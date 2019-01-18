import sys
sys.path.append('/afs/cern.ch/cms/PPD/PdmV/tools/McM/')
from rest import McM
from json import dumps

#set dev to False to run the final version of the script (i.e. send the modifications made to MCM)
#while editing keep dev set to True
mcm = McM(dev=False)

#list of requests to extend 
requests_to_extend = ['SUS-RunIIFall17FSPremix-00023', 'SUS-RunIIFall17FSPremix-00024', 'SUS-RunIIFall17FSPremix-00026', 'SUS-RunIIFall17FSPremix-00021',
                        'SUS-RunIIFall17FSPremix-00019', 'SUS-RunIIFall17FSPremix-00020', 'SUS-RunIIFall17FSPremix-00029', 'SUS-RunIIFall17FSPremix-00030',
                        'SUS-RunIIFall17FSPremix-00031', 'SUS-RunIIFall17FSPremix-00025', 'SUS-RunIIFall17FSPremix-00014', 'SUS-RunIIFall17FSPremix-00018',
                        'SUS-RunIIFall17FSPremix-00027', 'SUS-RunIIFall17FSPremix-00013', 'SUS-RunIIFall17FSPremix-00017', 'SUS-RunIIFall17FSPremix-00016',
                        'SUS-RunIIFall17FSPremix-00015'
                        ]

#write the prepids of the new cloned requests to a txt file
f = open('new_requests.txt', 'w')

for request_prepid_to_clone in requests_to_extend:
    
    print( 'Cloning and modifying {0}'.format(request_prepid_to_clone) )

    # Get a request object which we want to clone
    request = mcm.get('requests', request_prepid_to_clone)
   
    #clone request and print error if it fails 
    clone_answer = mcm.clone_request(request)
    if clone_answer.get('results'):
        pass
    else:
        print('Something went wrong while cloning a request. %s' % (dumps(clone_answer)))

    #write new prepid to file 
    f.write( clone_answer['prepid'] + '\n')
    
    #modify and update cloned request
    #note that these modifications must be done after cloning since they might otherwise be reset
    cloned_request = mcm.get('requests', clone_answer['prepid'] )

    total_events = request['total_events']
    modifications = {'extension': 1,
                     'total_events': int(total_events*1.5),
                     'process_string' : '',
                     'memory' : 4000,
                     'keep_output' : [False]
                     }
    
    # Make predefined modifications
    for key in modifications:
        cloned_request[key] = modifications[key]
   
    #update the cloned request
    update_response = mcm.update('requests', cloned_request)
    updated_clone = mcm.get('requests',  clone_answer['prepid'])
    
f.close()
