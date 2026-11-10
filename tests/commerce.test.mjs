import test from 'node:test';
import assert from 'node:assert/strict';
import { stat, readFile } from 'node:fs/promises';
import { cartTotal, changeQuantity, products, tracks } from '../src/data.ts';

test('mixed souvenir order totals match the checkout amount',()=>{
  let cart=changeQuantity({},'tote',2);
  cart=changeQuantity(cart,'poster',1);
  assert.equal(cartTotal(cart),385000);
  assert.equal(cartTotal(changeQuantity(cart,'tote',-1)),240000);
});
test('removing the last item yields an empty cart and zero total',()=>{
  const cart=changeQuantity({record:1},'record',-1);
  assert.deepEqual(cart,{});
  assert.equal(cartTotal(cart),0);
});
test('invalid product ids and excessive quantities cannot change the order price',()=>{
  const cart=changeQuantity({},'tote',100);
  assert.equal(cart.tote,20);
  assert.deepEqual(changeQuantity(cart,'unknown-product',1),cart);
  assert.deepEqual(changeQuantity(cart,'tote',-100),{});
});
test('every demo track has a full local MP3 and source attribution',async()=>{
  for(const track of tracks){
    assert.equal(track.license,track.additional?'CC BY-NC 4.0':'CC BY-SA 4.0');
    assert.equal(new URL(track.source).hostname,'www.classicals.de');
    const url=new URL('../public'+track.src,import.meta.url);
    assert.ok((await stat(url)).size>1000000,`${track.title} must be a complete recording`);
    const bytes=await readFile(url);
    assert.ok(bytes.toString('ascii',0,3)==='ID3'||(bytes[0]===255&&(bytes[1]&224)===224),`${track.title} must be MP3 audio`);
  }
  assert.equal(new Set(products.map(p=>p.id)).size,products.length);
});
