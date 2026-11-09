"""Keyboard pose control for MuJoCo. Anchored pelvis; NOT balance control."""
from pathlib import Path
import argparse,csv,queue,time
import numpy as np
import mujoco
ROOT=Path(__file__).resolve().parent

def target(model,pose,t):
    q=np.zeros(model.nu)
    def put(joint,value):
        idx=mujoco.mj_name2id(model,mujoco.mjtObj.mjOBJ_ACTUATOR,joint+'_servo')
        q[idx]=value
    if pose in ['guide','wave','both']:
        # Robot faces -X. Positive shoulder pitch raises the arm toward -X.
        put('left_shoulder_pitch',1.15)
        put('left_shoulder_roll',.35)
        put('left_elbow',.25)
    if pose=='wave':put('left_elbow',.6+.3*np.sin(2*np.pi*.65*t))
    if pose=='both':
        put('right_shoulder_pitch',1.15);put('right_shoulder_roll',-.35);put('right_elbow',.25)
    return np.clip(q,model.actuator_ctrlrange[:,0],model.actuator_ctrlrange[:,1])

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--scene',choices=['cabin','vestibule'],default='cabin')
    ap.add_argument('--pose',choices=['rest','guide','wave','both'],default='guide')
    ap.add_argument('--headless',action='store_true')
    ap.add_argument('--duration',type=float,default=10,help='Headless simulation duration in seconds')
    ap.add_argument('--csv',type=Path,default=ROOT/'joint_log.csv')
    args=ap.parse_args()
    model=mujoco.MjModel.from_xml_path(str(ROOT/('02_cabin_control.xml' if args.scene=='cabin' else '01_vestibule_control.xml')))
    data=mujoco.MjData(model);mujoco.mj_forward(model,data)
    commands=queue.SimpleQueue();state={'pose':args.pose,'paused':False};dt=model.opt.timestep
    names=[mujoco.mj_id2name(model,mujoco.mjtObj.mjOBJ_JOINT,i) for i in range(model.njnt)]
    print('ANCHORED JOINT DEMO / pelvis fixed, no train disturbances or balance controller')
    print('Focus the viewer, then: 0 rest | 1 exit guide | 2 wave | 3 both arms | R reset | SPACE pause/resume')
    args.csv.parent.mkdir(parents=True,exist_ok=True)
    with args.csv.open('w',newline='',encoding='utf-8') as f:
        writer=csv.writer(f);writer.writerow(['time_s','pose',*['q_'+n+'_rad' for n in names],*['target_'+n+'_rad' for n in names]])
        def tick():
            while not commands.empty():
                key=commands.get()
                if key in [48,49,50,51]:state['pose']=['rest','guide','wave','both'][key-48]
                elif key in [82,114]:
                    mujoco.mj_resetData(model,data);mujoco.mj_forward(model,data);state['pose']='rest'
                elif key==32:state['paused']=not state['paused']
            if state['paused']:return
            ref=target(model,state['pose'],data.time)
            # Rate limit reference motion to avoid abrupt jumps (0.9 rad/s).
            data.ctrl[:]+=np.clip(ref-data.ctrl,-.9*dt,.9*dt)
            mujoco.mj_step(model,data)
            if round(data.time/dt)%25==0:
                writer.writerow([data.time,state['pose'],*data.qpos,*data.ctrl])
        if args.headless:
            for _ in range(int(args.duration/dt)):tick()
            print(f'Headless run complete: {data.time:.3f} s, log {args.csv}')
        else:
            from mujoco import viewer as mjviewer
            with mjviewer.launch_passive(model,data,key_callback=commands.put,show_left_ui=True,show_right_ui=True) as viewer:
                viewer.cam.azimuth=180;viewer.cam.elevation=-15;viewer.cam.distance=4.2;viewer.cam.lookat[:]=[0,0,1.1]
                while viewer.is_running():
                    start=time.perf_counter()
                    # Batch several physics steps per UI refresh, retaining real-time pacing.
                    with viewer.lock():
                        for _ in range(5):tick()
                    viewer.sync()
                    time.sleep(max(0,5*dt-(time.perf_counter()-start)))

if __name__=='__main__':main()
