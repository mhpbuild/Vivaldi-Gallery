import test from 'node:test';
import assert from 'node:assert/strict';
import { walkStep,blocked } from '../src/navigation.ts';
const input={forward:1,strafe:0,yaw:0,delta:.05};
test('W walks forward along the camera heading and D strafes independently',()=>{
  const start={x:0,z:30};
  assert.ok(walkStep(start,input).z<start.z);
  assert.ok(walkStep(start,{...input,forward:0,strafe:1}).x>start.x);
  assert.ok(walkStep(start,{...input,yaw:Math.PI/2}).x<start.x);
});
test('diagonal walking is normalized and Shift increases walking speed',()=>{
  const start={x:0,z:30};
  const straight=walkStep(start,input),diagonal=walkStep(start,{...input,strafe:1});
  assert.ok(Math.abs(Math.hypot(straight.x,straight.z-30)-Math.hypot(diagonal.x,diagonal.z-30))<1e-9);
  assert.ok(walkStep(start,{...input,fast:true}).z<straight.z);
});
test('walking cannot pass through the wall or center sculpture',()=>{
  let wall={x:9.5,z:14};for(let i=0;i<100;i++)wall=walkStep(wall,{...input,forward:0,strafe:1});
  assert.equal(wall.x,9.65);
  let statue={x:0,z:27};for(let i=0;i<100;i++)statue=walkStep(statue,input);
  assert.ok(statue.z>=25.3);assert.equal(blocked(statue.x,statue.z),false);
});
test('browser stalls cannot cause collision tunneling',()=>{
  const step=walkStep({x:0,z:27},{...input,delta:5,fast:true});
  assert.ok(step.z>26.7);
});
