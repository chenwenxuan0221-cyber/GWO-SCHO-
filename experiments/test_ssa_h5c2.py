"""H5c2 structural audit for source-structured SSA."""
from __future__ import annotations
import numpy as np
from algorithms.ssa import ssa, _matlab_style_initialization
from benchmarks.classic_23 import get_benchmark

ANCHORS=("F2","F7","F15","F21")
N=6
MAX_ITER=40
SEED=1000
OBJ_BASE=5_032_000

def make(name):
    b=get_benchmark(name)
    return b,b.make_objective(seed=OBJ_BASE+int(name[1:]))

def check_init():
    r1=np.random.default_rng(1234)
    a=_matlab_style_initialization(4,3,-2.0,5.0,r1)
    r2=np.random.default_rng(1234)
    b=r2.random((4,3))*7.0-2.0
    assert np.array_equal(a,b)
    lo=np.array([-2.,-1.,0.]); hi=np.array([2.,3.,5.])
    r3=np.random.default_rng(4321)
    a=_matlab_style_initialization(4,3,lo,hi,r3)
    r4=np.random.default_rng(4321)
    b=np.empty((4,3))
    for j in range(3): b[:,j]=r4.random(4)*(hi[j]-lo[j])+lo[j]
    assert np.array_equal(a,b)

def validate(name,b,run):
    score,pos,curve,d=run
    pos=np.asarray(pos); curve=np.asarray(curve)
    assert np.isfinite(score) and np.all(np.isfinite(pos)) and np.all(np.isfinite(curve))
    assert pos.shape==(b.dim,) and curve.shape==(MAX_ITER,)
    assert curve[0]==0.0
    assert np.all(np.diff(curve[1:])<=0.0)
    assert score==float(curve[-1])
    leaders=N//2
    exp_lead=(MAX_ITER-1)*leaders*b.dim
    assert d["objective_evaluations"]==N*MAX_ITER
    assert d["leader_coordinate_updates"]==exp_lead
    assert d["follower_vector_updates"]==(MAX_ITER-1)*(N-leaders)
    assert d["leader_random_draws"]==2*exp_lead
    assert d["c3_less_half"]+d["c3_ge_half"]==exp_lead
    assert d["first_c1"]==2.0*np.exp(-((8.0/MAX_ITER)**2))
    assert d["last_c1"]==2.0*np.exp(-16.0)

def main():
    print("="*124)
    print("H5c2 - SSA source-structured Python translation audit")
    print("="*124)
    print(f"Anchors: {','.join(ANCHORS)} | N={N} | MaxIter={MAX_ITER} | optimizer seed={SEED}")
    print("No formal 30-run comparison will be executed.")
    print("algorithms/gwo.py and algorithms/scho.py will NOT be modified.")
    print("="*124)

    print("\n1) Initialization + leader/follower structure audit")
    check_init()
    b,obj=make("F2")
    *_,d=ssa(obj,b.dim,b.lb,b.ub,5,4,seed=123,return_diagnostics=True)
    assert d["leader_count"]==2
    assert d["follower_vector_updates"]==9
    print("Initialization and floor(N/2) leader rule PASS")

    print("\n2) Determinism + source-structure audit")
    for name in ANCHORS:
        b,o1=make(name)
        a=ssa(o1,b.dim,b.lb,b.ub,N,MAX_ITER,seed=SEED,return_diagnostics=True)
        _,o2=make(name)
        c=ssa(o2,b.dim,b.lb,b.ub,N,MAX_ITER,seed=SEED,return_diagnostics=True)
        validate(name,b,a)
        assert a[0]==c[0]
        assert np.array_equal(a[1],c[1]) and np.array_equal(a[2],c[2]) and a[3]==c[3]
        d=a[3]
        print(f"{name:<4} D={b.dim:<2} best={a[0]:>14.8g} evals={d['objective_evaluations']:<4} "
              f"leader_coord={d['leader_coordinate_updates']:<5} followers={d['follower_vector_updates']:<4} "
              f"c3<.5/>=.5={d['c3_less_half']}/{d['c3_ge_half']} PASS")

    print("\n3) Guard audit")
    b,obj=make("F2")
    try:
        ssa(obj,b.dim,b.lb,b.ub,1,MAX_ITER,seed=SEED)
    except ValueError:
        print("N<2 rejected PASS")
    else:
        raise AssertionError("N<2 was not rejected")

    print("-"*124)
    print("H5c2 RESULT: PASS")
    print("SSA source structure is preserved in the Python port.")
    print("Sequential follower update and curve[0]=0 source quirks are preserved.")
    print("NumPy RNG is used; no MATLAB bitwise/random-stream equivalence is claimed.")
    print("Next: H5c3 implement/test GJO only.")
    print("="*124)

if __name__=="__main__":
    main()
