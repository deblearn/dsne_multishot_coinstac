#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import sys
from tsneFunctions import normalize_columns, tsne, listRecursive
import json


def remote_1(args):
    ''' It will receive parameters from dsne_multi_shot.
    After receiving parameters it will compute tsne on high
    dimensional remote data and pass low dimensional values
    of remote site data


       args (dictionary): {
            "shared_X" (str):  remote site data
            "shared_Label" (str): remote site labels
            "no_dims" (int): Final plotting dimensions
            "initial_dims" (int): number of dimensions that PCA should produce
            "perplexity" (int): initial guess for nearest neighbor
            "max_iter" (str):  maximum number of iterations during
                                tsne computation
            }
       computation_phase (string): remote

       normalize_columns:
           Shared data is normalized through this function

       Returns:
           Return args will contain previous args value in
           addition of Y[low dimensional Y values] values of shared_Y.
       args(dictionary):  {
           "shared_X" (str):  remote site data,
           "shared_Label" (str):  remote site labels
           "no_dims" (int): Final plotting dimensions,
           "initial_dims" (int): number of dimensions that PCA should produce
           "perplexity" (int): initial guess for nearest neighbor
           "shared_Y" : the low-dimensional remote site data
           }
       '''

    shared_X = np.loadtxt('test/input/simulatorRun/shared_x.txt')
    #    shared_Labels = np.loadtxt('test/input/simulatorRun/shared_y.txt')

    no_dims = args["input"]["local0"]["no_dims"]
    initial_dims = args["input"]["local0"]["initial_dims"]
    perplexity = args["input"]["local0"]["perplexity"]
    max_iter = args["input"]["local0"]["max_iterations"]

    shared_X = normalize_columns(shared_X)
    (sharedRows, sharedColumns) = shared_X.shape

    init_Y = np.random.randn(sharedRows, no_dims)

    shared_Y = tsne(
        shared_X,
        init_Y,
        sharedRows,
        no_dims,
        initial_dims,
        perplexity,
        computation_phase="remote")

    computation_output = {
        "output": {
            "shared_y": shared_Y.tolist(),
            "computation_phase": 'remote_1',
        },
        "cache": {
            "shared_y": shared_Y.tolist(),
            "max_iterations": max_iter
        }
    }

    return json.dumps(computation_output)


def remote_2(args):
    '''
    args(dictionary):  {
        "shared_X"(str): remote site data,
        "shared_Label"(str): remote site labels
        "no_dims"(int): Final plotting dimensions,
        "initial_dims"(int): number of dimensions that PCA should produce
        "perplexity"(int): initial guess for nearest neighbor
        "shared_Y": the low - dimensional remote site data

    Returns:
        Y: the final computed low dimensional remote site data
        local1Yvalues: Final low dimensional local site 1 data
        local2Yvalues: Final low dimensional local site 2 data
    }
    '''
    Y =  np.array(args["cache"]["shared_y"])
    average_Y = (np.mean(Y, 0))
    average_Y[0] = 0
    average_Y[1] = 0
    C = 0

    compAvgError = {'avgX': average_Y[0], 'avgY': average_Y[1], 'error': C}

    computation_output = \
    {
        "output": {
            "compAvgError": compAvgError,
            "computation_phase": 'remote_2',
            "shared_Y": Y.tolist(),
            "number_of_iterations": 0

                },

        "cache": {
            "compAvgError": compAvgError,
            "number_of_iterations": 0
        }
    }

    return json.dumps(computation_output)


def remote_3(args):
    iteration =  args["cache"]["number_of_iterations"]
    iteration +=1;
    C = args["cache"]["compAvgError"]["error"]

    #Y = args["input"]["local_Y"]

    #average_Y = (np.mean(Y, 0))
    average_Y = [0]*2
    C = 0
    #avg_beta_vector = np.mean([input_list[site]["beta_vector_local"] for site in input_list], axis=0)

    average_Y[0] = np.mean([args['input'][site]['MeanX'] for site in args["input"]])
    average_Y[1] = np.mean([args['input'][site]['MeanY'] for site in args["input"]])

    average_Y = np.array(average_Y)
    C = C + np.mean([args['input'][site]['error'] for site in args["input"]])

    meanY = np.mean([args["input"][site]["local_Shared_Y"] for site in args["input"]], axis=0)
    meaniY = np.mean([args["input"][site]["local_Shared_iY"] for site in args["input"]], axis=0)

    Y = meanY + meaniY


    Y -= np.tile(average_Y, (Y.shape[0], 1))

    compAvgError = {'avgX': average_Y[0], 'avgY': average_Y[1], 'error': C}

    if(iteration == 6):
        raise Exception('In remote_3 after iterations 6')

    if(iteration<10):
        phase = 'remote_2';
    else:
        phase = 'remote_3';


    if iteration == 5:
        shared_labels = np.loadtxt('test/input/simulatorRun/shared_y.txt')
        concat_Y = []
        concat_local_Y_labels = []

        concat_Y.append(Y)
        concat_local_Y_labels.append(shared_labels)
        #concat_local_Y_labels =  np.concatenate(concat_local_Y_labels,shared_labels)


        for site in args["input"]:
            #raise Exception(type(args["input"][site]["local_Y"]))
            #concat_Y.np.concatenate(args['input'][site]["local_Y"])
            concat_Y.append(args["input"][site]["local_Y"])
            concat_local_Y_labels.append(args["input"][site]["local_Y_labels"])

            #np.concatenate( (concat_Y, args['input'][site]["local_Y"]),  axis=0 )
            #np.concatenate((concat_local_Y_labels, args["input"][site]["local_Y_labels"]), axis=0)
            #concat_local_Y_labels.np.concatenate(args["input"][site]["local_Y_labels"])

        filepath = 'test/remote/output/simulatorRun/lowdimembed.txt'
        f = open(filepath, 'w+')
        for line1, line2 in zip(concat_Y, concat_local_Y_labels):
            f.writelines(([ str(line1), str(line2)]))
        f.close()
        #concat_Y =  [int(i) for i in concat_Y]
        #concat_local_Y_labels = [int(j) for j in concconcat_local_Y_labelsat_Y]

        raise Exception( concat_Y, concat_local_Y_labels)


    else:

        computation_output = {"output": {
                                "compAvgError": compAvgError,
                                "number_of_iterations": 0,
                                "shared_Y": Y.tolist(),
                                "computation_phase": phase},

                                "cache": {
                                    "compAvgError": compAvgError,
                                    "number_of_iterations": iteration
                                }
                            }


    return json.dumps(computation_output)


def remote_4(args):

    # Final aggregation step
    computation_output = {"output": {"final_embedding": 0}, "success": True}
    return json.dumps(computation_output)


if __name__ == '__main__':

    np.random.seed(0)
    parsed_args = json.loads(sys.argv[1])

    phase_key = list(listRecursive(parsed_args, 'computation_phase'))

    if 'local_noop' in phase_key:
        computation_output = remote_1(parsed_args)
        sys.stdout.write(computation_output)
    elif 'local_1' in phase_key:
        computation_output = remote_2(parsed_args)
        sys.stdout.write(computation_output)
    elif 'local_2' in phase_key:
        computation_output = remote_3(parsed_args)
        sys.stdout.write(computation_output)
    elif 'local_3' in phase_key:
        computation_output = remote_4(parsed_args)
        sys.stdout.write(computation_output)
    else:
        raise ValueError("Error occurred at Remote")
