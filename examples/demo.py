#! /usr/bin/env python

# GPTune Copyright (c) 2019, The Regents of the University of California,
# through Lawrence Berkeley National Laboratory (subject to receipt of any
# required approvals from the U.S.Dept. of Energy) and the University of
# California, Berkeley.  All rights reserved.
#
# If you have questions about your rights to use or distribute this software,
# please contact Berkeley Lab's Intellectual Property Office at IPO@lbl.gov.
#
# NOTICE. This Software was developed under funding from the U.S. Department
# of Energy and the U.S. Government consequently retains certain rights.
# As such, the U.S. Government has been granted for itself and others acting
# on its behalf a paid-up, nonexclusive, irrevocable, worldwide license in
# the Software to reproduce, distribute copies to the public, prepare
# derivative works, and perform publicly and display publicly, and to permit
# other to do so.
#


################################################################################

from autotune.search import *
from autotune.space import *
from autotune.problem import *
from gptune import GPTune
from data import Data
from options import Options
from computer import Computer
import sys
import os
import mpi4py
from mpi4py import MPI
import numpy as nps
sys.path.insert(0, os.path.abspath(__file__ + "/../../GPTune/"))

# from GPTune import *

################################################################################

# Define Problem

# YL: for the spaces, the following datatypes are supported:
# Real(lower, upper, transform="normalize", name="yourname")
# Integer(lower, upper, transform="normalize", name="yourname")
# Categoricalnorm(categories, transform="onehot", name="yourname")


# Argmin{x} objective(t,x), for x in [0., 1.]


input_space = Space([Real(0., 10., transform="normalize", name="t")])
parameter_space = Space([Real(0., 1., transform="normalize", name="x")])

# input_space = Space([Real(0., 0.0001, "uniform", "normalize", name="t")])
# parameter_space = Space([Real(-1., 1., "uniform", "normalize", name="x")])


output_space = Space([Real(float('-Inf'), float('Inf'), name="time")])


def objective(point):
    """
    f(t,x) = exp(- (x + 1) ^ (t + 1) * cos(2 * pi * x)) * (sin( (t + 2) * (2 * pi * x) ) + sin( (t + 2)^(2) * (2 * pi * x) + sin ( (t + 2)^(3) * (2 * pi *x))))
    """

    t = point['t']
    x = point['x']
    a = 2 * np.pi
    b = a * t
    c = a * x
    d = np.exp(- (x + 1) ** (t + 1)) * np.cos(c)
    e = np.sin((t + 2) * c) + np.sin((t + 2)**2 * c) + np.sin((t + 2)**3 * c)
    f = d * e

    """
    f(t,x) = x^2+t
    """
    # t = point['t']
    # x = point['x']
    # f = 20*x**2+t

    return f


constraints = {"cst1": "x >= 0. and x <= 1."}
print('demo before TuningProblem')
problem = TuningProblem(input_space, parameter_space,output_space, objective, constraints, None)

# Run Autotuning

#search_param_dict = {}
#search_param_dict['method'] = 'MLA'
#
#search = Search(problem, search_param_dict)
#
# search.run()


if __name__ == '__main__':
    computer = Computer(nodes=1, cores=16, hosts=None)
    options = Options()
    options['model_restarts'] = 1

    options['distributed_memory_parallelism'] = False
    options['shared_memory_parallelism'] = False

    options['model_processes'] = 1
    # options['model_threads'] = 1
    # options['model_restart_processes'] = 1

    # options['search_multitask_processes'] = 1
    # options['search_multitask_threads'] = 1
    # options['search_threads'] = 1


    # options['mpi_comm'] = None
    #options['mpi_comm'] = mpi4py.MPI.COMM_WORLD
    options['model_class'] = 'Model_LCM'
    options['verbose'] = False
    # options['sample_algo'] = 'MCS'
    # options['sample_class'] = 'SampleOpenTURNS'
        

    options.validate(computer=computer)
    data = Data(problem)
    gt = GPTune(problem, computer=computer, data=data, options=options)
    # print('demo before MLA')
    NI=20
    NS=10
    (data, modeler, stats) = gt.MLA(NS=NS, NI=NI, NS1=NS-1)


    """ Print all input and parameter samples """
    for tid in range(NI):
        print("tid: %d" % (tid))
        print("    t:%d " % (data.I[tid][0]))
        print("    Ps ", data.P[tid])
        print("    Os ", data.O[tid])
        print('    Popt ', data.P[tid][np.argmin(data.O[tid])], 'Yopt ', min(data.O[tid])[0])
        
    print("stats: ", stats)
