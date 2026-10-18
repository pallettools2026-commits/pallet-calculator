from pathlib import Path
import re

index = Path('index.html')
s = index.read_text(encoding='utf-8')

shared = 'const pallet3DState=window.pallet3DState||(window.pallet3DState={angle:-28,mode:"3d",selected:"all",dragging:false,startX:0,startAngle:-28,pointerId:null});'
local = 'const pallet3DState={angle:-28,mode:"3d",selected:"all",dragging:false,startX:0,startAngle:-28,pointerId:null};'
if shared in s:
    s = s.replace(shared, local, 1)

s, n = re.subn(r'assets/pallet3d-v10\.js\?v=\d+', 'assets/pallet3d-v10.js?v=151', s, count=1)
if n != 1:
    raise SystemExit('pallet3d cache reference not found')
index.write_text(s, encoding='utf-8')

p = Path('assets/pallet3d-v10.js')
j = p.read_text(encoding='utf-8')

old_active = "active={renderer,scene,camera,groups,mode,signature:currentSignature(),draw,profile};"
new_active = "active={renderer,scene,camera,groups,mode,signature:currentSignature(),draw,profile,rotateByDegrees:(degrees=45)=>{yaw+=num(degrees,45)*Math.PI/180;state.angle=yaw*180/Math.PI;draw();}};"
if old_active not in j:
    if 'rotateByDegrees:(degrees=45)' not in j:
        raise SystemExit('active scene anchor not found')
else:
    j = j.replace(old_active, new_active, 1)

anchor = "  function setupLivePalletDimensions(){\n"
setup = r'''  function setupNativeViewControls(){
    const rotate=el('rotatePallet');
    if(rotate&&rotate.dataset.threeControlReady!=='1'){
      rotate.dataset.threeControlReady='1';
      rotate.textContent='↻ Повернуть на 45°';
      rotate.addEventListener('click',e=>{
        e.preventDefault();e.stopImmediatePropagation();
        if(state.mode==='top'||state.mode==='side'){
          state.assemblyStep=0;
          state.mode='3d';
          state.angle=(num(state.angle,-34)+45)%360;
          render(num(el('pL')?.value),num(el('pW')?.value));
          return;
        }
        if(active?.rotateByDegrees){active.rotateByDegrees(45);return;}
        state.angle=(num(state.angle,-34)+45)%360;
        render(num(el('pL')?.value),num(el('pW')?.value));
      },true);
    }
    const reset=el('resetPalletView');
    if(reset&&reset.dataset.threeControlReady!=='1'){
      reset.dataset.threeControlReady='1';
      reset.addEventListener('click',e=>{
        e.preventDefault();e.stopImmediatePropagation();
        state.angle=-34;state.mode='3d';state.selected='all';state.assemblyStep=0;
        el('previewStage')?.classList.remove('zoomed');
        render(num(el('pL')?.value),num(el('pW')?.value));
      },true);
    }
  }

'''
if 'function setupNativeViewControls()' not in j:
    if anchor not in j:
        raise SystemExit('setup controls anchor not found')
    j = j.replace(anchor, setup + anchor, 1)

old_init = "setupDeckCountControl();setupLivePalletDimensions();setupAdminEmployeeDelete();"
new_init = "setupNativeViewControls();setupDeckCountControl();setupLivePalletDimensions();setupAdminEmployeeDelete();"
if old_init in j:
    j = j.replace(old_init, new_init, 1)
elif new_init not in j:
    raise SystemExit('initialization anchor not found')

p.write_text(j, encoding='utf-8')
print('Three.js 45-degree rotation control fixed')
