"""Reproducible planar balance model. All generated measurements are synthetic."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parent
DT=.01
M,H,G=60.,.90,9.81
I=M*H*H
FOOT_HALF=.14
TAU_MAX=M*G*FOOT_HALF
SCENARIOS=[('quiet',.015,1.2,65,0),('low',.12,1.8,78,0),('high',1.3,2.4,95,0),('shock',1.3,2.4,100,95),('noise_only',0.,1.8,105,0),('nearby_object',0.,1.8,85,0)]

def run(name='high',controller='adaptive',seed=42,duration=10.,amplitude=None,frequency=None):
    _,a,f,db,push=next(s for s in SCENARIOS if s[0]==name)
    if amplitude is not None:a=amplitude
    if frequency is not None:f=frequency
    rng=np.random.default_rng(seed);theta=0.;omega=0.;slip=0.;vel=0.;fallen=False;rows=[]
    # Identical disturbance draws for both controllers; initial IMU perturbation.
    theta=float(rng.normal(0,.001));ph=float(rng.uniform(-.2,.2))
    for t in np.arange(0,duration,DT):
        accel=a*(np.sin(2*np.pi*f*t+ph)+.18*np.sin(2*np.pi*7*t))
        force=push if 4.0<=t<4.18 else 0.
        obj=.095*np.sin(2*np.pi*1.25*t) if name=='nearby_object' else .012*np.sin(2*np.pi*f*t)
        kp,kd=(650.,100.) if controller=='baseline' else (1600.,460.)
        ff=M*H*accel if controller=='adaptive' else 0.
        torque=float(np.clip(-kp*theta-kd*omega+ff,-TAU_MAX,TAU_MAX))
        # Planar inverted pendulum, angle measured relative to vertical.
        alpha=(M*G*H*np.sin(theta)-M*H*accel*np.cos(theta)+force*H+torque)/I
        if not fallen:
            omega+=alpha*DT;theta+=omega*DT
            if abs(theta)>=np.deg2rad(35):fallen=True
        else:
            # Absorbing failure state, not a rigid-body ground-contact simulation.
            theta=float(np.sign(theta)*np.deg2rad(35));omega=0.
        demand=M*abs(accel)+abs(force)
        excess=max(0.,demand-.65*M*G)
        vel=vel*.97+np.sign(accel+force/M)*excess/M*DT
        slip+=vel*DT
        # Swept shoulder envelope versus nearest moving obstacle edge.
        clearance=.58-obj-(abs(H*np.sin(theta)+slip)+.20)
        rows.append((t,name,controller,seed,accel,db,np.rad2deg(theta),omega,torque,force,obj,slip,clearance,fallen,clearance<=0,'synthetic_simulation'))
    return pd.DataFrame(rows,columns=['time_s','scenario','controller','seed','floor_accel_m_s2','sound_dba','tilt_deg','angular_velocity_rad_s','ankle_torque_nm','push_force_n','object_displacement_m','foot_slip_m','clearance_m','fallen','collision','data_origin'])

def summary(d):
    post=d[d.time_s>=4.18];recovery=np.nan
    if d.push_force_n.max()>0:
        stable=(post.tilt_deg.abs()<2).to_numpy()
        for i in range(len(stable)-49):
            if stable[i:i+50].all():recovery=float(post.time_s.iloc[i]-4.18);break
    return dict(scenario=d.scenario.iloc[0],controller=d.controller.iloc[0],seed=int(d.seed.iloc[0]),peak_tilt_deg=float(d.tilt_deg.abs().max()),rms_tilt_deg=float(np.sqrt(np.mean(d.tilt_deg**2))),peak_floor_accel_m_s2=float(d.floor_accel_m_s2.abs().max()),recovery_s=recovery,fallen=bool(d.fallen.any()),collision=bool(d.collision.any()),max_slip_m=float(d.foot_slip_m.abs().max()),min_clearance_m=float(d.clearance_m.min()),data_origin='synthetic_simulation')

def main():
    records=[];history=[]
    for name,*_ in SCENARIOS:
        for ctrl in ['baseline','adaptive']:
            for seed in range(20):
                d=run(name,ctrl,seed);history.append(summary(d))
                if seed==0:records.append(d)
    pd.concat(records).to_csv(ROOT/'data/timeseries.csv',index=False)
    hist=pd.DataFrame(history);hist.to_csv(ROOT/'data/experiment_history_SYNTHETIC.csv',index=False)
    agg=hist.groupby(['scenario','controller']).agg(trials=('seed','size'),mean_peak_tilt_deg=('peak_tilt_deg','mean'),fall_rate=('fallen','mean'),collision_rate=('collision','mean'),mean_recovery_s=('recovery_s','mean')).reset_index()
    agg.to_csv(ROOT/'data/summary.csv',index=False)
    payload={}
    for name,*_ in SCENARIOS:
        payload[name]={}
        for ctrl in ['baseline','adaptive']:
            d=run(name,ctrl,0).iloc[::5]
            payload[name][ctrl]=d[['time_s','tilt_deg','floor_accel_m_s2','sound_dba','object_displacement_m','clearance_m','fallen','collision']].to_dict('records')
    (ROOT/'data/playback.json').write_text(json.dumps(payload),encoding='utf-8')
    print(agg.to_string(index=False))
if __name__=='__main__':main()
