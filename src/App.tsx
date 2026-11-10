import { lazy, Suspense, useEffect, useRef, useState } from 'react';
import { ArrowDown, ArrowRight, ArrowUpRight, Check, ChevronLeft, ChevronRight, CircleHelp, Maximize, Minimize, Minus, Music2, Pause, Play, Plus, Repeat, RotateCcw, ShoppingBag, Shuffle, SkipBack, SkipForward, Volume2, VolumeX, X } from 'lucide-react';
import { cartTotal, changeQuantity, products, rupiah, stops, tracks, seasons, shopStop } from './data';
import type { Cart, Product, Track } from './data';
import SeasonCollection, { TrackArtwork, SeasonCard, VivaldiAbout } from './SeasonCollection';
const Gallery=lazy(()=>import('./Gallery'));
type Panel='collection'|'shop'|'cart'|'about'|null;
const timeLabel=(seconds:number)=>Number.isFinite(seconds)?`${Math.floor(seconds/60)}:${Math.floor(seconds%60).toString().padStart(2,'0')}`:'0:00';
function loadCart():Cart {
  try { const saved=JSON.parse(localStorage.getItem('ruang-dengar-cart')||'{}');return Object.fromEntries(products.filter(p=>Number.isInteger(saved[p.id])&&saved[p.id]>0).map(p=>[p.id,Math.min(saved[p.id],20)])); } catch{return {};}
}
function Soundmark(){return <span className="soundmark renaissance-seal" aria-hidden="true"><svg viewBox="0 0 60 60" fill="none"><circle cx="30" cy="30" r="27"/><circle cx="30" cy="30" r="23" strokeWidth=".5"/><path d="M13 30h34M30 7v46M14 14l32 32M46 14L14 46" strokeWidth=".35"/><path d="M20 19c-8 2-3 19 3 22h14c6-3 11-20 3-22M19 24h22M23 24l3 17m4-17v17m7-17-3 17M21 43h18" strokeWidth="1.5"/><circle cx="30" cy="30" r="17" strokeWidth=".4"/></svg></span>;}


function ProductArt({product}:{product:Product}){return <div className={`product-art product-${product.id}`} aria-hidden="true"><span className="product-object"><span className="product-wordmark">VIVALDI<br/>1725<span className="product-waves">(( • ))</span></span></span><span className="product-caption">LE QUATTRO STAGIONI.</span></div>;}

export default function App(){
  const [entered,setEntered]=useState(true),[stop,setStop]=useState(0),[panel,setPanel]=useState<Panel>(null);
  const [viewVersion,setViewVersion]=useState(0),[roaming,setRoaming]=useState(false);
  const [collectionSeason,setCollectionSeason]=useState('all');
  const [library,setLibrary]=useState<Track[]>(tracks),[current,setCurrent]=useState<Track>(tracks[0]);
  const [playing,setPlaying]=useState(false),[loading,setLoading]=useState(false),[audioError,setAudioError]=useState('');
  const [elapsed,setElapsed]=useState(0),[duration,setDuration]=useState(tracks[0].seconds||0),[volume,setVolume]=useState(.65),[muted,setMuted]=useState(false);
  const [shuffle,setShuffle]=useState(false),[repeat,setRepeat]=useState(false),[cart,setCart]=useState<Cart>(loadCart);
  const [notice,setNotice]=useState(''),[checkingOut,setCheckingOut]=useState(false),[order,setOrder]=useState<{id:string;total:number}|null>(null);
  const [fullscreen,setFullscreen]=useState(false),[uploadError,setUploadError]=useState('');
  const audio=useRef<HTMLAudioElement>(null),dialog=useRef<HTMLDialogElement>(null);
  const objectUrls=useRef<string[]>([]),checkoutTimer=useRef<ReturnType<typeof setTimeout>|undefined>(undefined),noticeTimer=useRef<ReturnType<typeof setTimeout>|undefined>(undefined);
  const count=Object.values(cart).reduce((sum,q)=>sum+q,0);
  const index=library.findIndex(t=>t.id===current.id);
  useEffect(()=>{try{localStorage.setItem('ruang-dengar-cart',JSON.stringify(cart));}catch{/* Private browsing still supports the session cart. */}},[cart]);
  useEffect(()=>{const d=dialog.current;if(panel&&d){if(!d.open)d.showModal();d.scrollTop=0;d.querySelector<HTMLButtonElement>('.close-button')?.focus();}else if(!panel&&d?.open)d.close();},[panel,order]);
  useEffect(()=>{const update=()=>setFullscreen(Boolean(document.fullscreenElement));document.addEventListener('fullscreenchange',update);return()=>document.removeEventListener('fullscreenchange',update);},[]);
  useEffect(()=>()=>{objectUrls.current.forEach(url=>URL.revokeObjectURL(url));clearTimeout(checkoutTimer.current);clearTimeout(noticeTimer.current);},[]);
  function announce(message:string){setNotice(message);clearTimeout(noticeTimer.current);noticeTimer.current=setTimeout(()=>setNotice(''),4000);}
  function openPanel(value:Panel){setPanel(value);setOrder(null);if(value==='collection')setCollectionSeason('all');}
  function browseSeason(id:string){setCollectionSeason(id);setPanel('collection');setOrder(null);}
  function chooseTrack(track:Track){if(current.id===track.id)togglePlay();else selectTrack(track);}
  function navigate(value:number){setStop(value);setViewVersion(v=>v+1);setRoaming(false);setEntered(true);if(value===shopStop)openPanel('shop');}
  async function playAudio(){
    if(!audio.current)return;setAudioError('');setLoading(true);
    try{await audio.current.play();}catch{setLoading(false);setPlaying(false);setAudioError('Audio belum bisa diputar. Coba lagi atau pilih lagu lain.');}
  }
  function togglePlay(){if(loading)return;if(playing){audio.current?.pause();}else void playAudio();}
  function selectTrack(track:Track,autoplay=true){
    if(!audio.current)return;
    if(current.id===track.id){if(autoplay)void playAudio();return;}
    audio.current.pause();audio.current.src=track.src;audio.current.load();setCurrent(track);setElapsed(0);setDuration(0);setAudioError('');
    if(autoplay)void playAudio();
  }
  function nextTrack(direction:number){const next=shuffle&&library.length>1?(index+1+Math.floor(Math.random()*(library.length-1)))%library.length:(index+direction+library.length)%library.length;selectTrack(library[next]);}
  function addToCart(product:Product){setCart(old=>changeQuantity(old,product.id,1));announce(`${product.name} ditambahkan ke tas.`);}
  function checkout(){if(!count||checkingOut)return;setCheckingOut(true);const total=cartTotal(cart);checkoutTimer.current=setTimeout(()=>{setOrder({id:`RD-${Date.now().toString(36).toUpperCase()}`,total});setCart({});setCheckingOut(false);},700);}
  async function toggleFullscreen(){try{if(document.fullscreenElement)await document.exitFullscreen();else await document.documentElement.requestFullscreen();}catch{announce('Layar penuh tidak didukung browser ini.');}}
  function uploadMusic(files:FileList|null){
    if(!files?.length)return;setUploadError('');const added:Track[]=[];
    Array.from(files).slice(0,10).forEach((file,i)=>{if(!file.type.startsWith('audio/')&&!/\.(mp3|wav|ogg|m4a|flac)$/i.test(file.name)){setUploadError('Pilih file audio MP3, WAV, OGG, M4A, atau FLAC.');return;}if(file.size>100*1024*1024){setUploadError('Maksimal 100 MB per lagu.');return;}const url=URL.createObjectURL(file);objectUrls.current.push(url);added.push({id:`local-${Date.now()}-${i}`,title:file.name.replace(/\.[^.]+$/,''),artist:'Musik Anda',genre:'Koleksi pribadi',duration:'—',src:url,color:'#54685c',description:'File lokal dari perangkat Anda. Tidak diunggah ke server dan hanya tersedia selama halaman ini terbuka.',license:'File pribadi',local:true});});
    if(added.length){setLibrary(old=>[...old,...added]);selectTrack(added[0]);announce(`${added.length} lagu pribadi siap didengarkan.`);}
  }
  return <div className={`app ${entered?'is-exploring':''}`}>
    <a className="skip-link" href="#room-navigation">Lewati ke navigasi ruang</a>
    <header className="site-header">
      <button className="brand" onClick={()=>{navigate(0);setPanel(null);}} aria-label="Ars Sonora, kembali ke aula"><Soundmark/><span>ARS SONORA<small>THE FOUR SEASONS</small></span></button>
      <div className="header-edition"><span>ANTONIO VIVALDI · 1678–1741</span><span>LE QUATTRO STAGIONI · VENEZIA, 1725</span></div>
      <nav aria-label="Navigasi utama"><button className={panel==='collection'?'active':''} onClick={()=>openPanel('collection')}>Koleksi musik <span className="nav-count">{library.length.toString().padStart(2,'0')}</span></button><button className="about-nav" onClick={()=>openPanel('about')}>Tentang ruang <ArrowUpRight size={15}/></button></nav>
      <button className="bag-button" onClick={()=>openPanel('cart')} aria-label={`Buka tas belanja, ${count} barang`}><ShoppingBag size={19}/><span className="bag-label">Tas</span><span className="bag-count">{count}</span></button>
    </header>
    <main id="main-content" className="experience">
      <Suspense fallback={<div className="scene-status">Menyiapkan ruang…</div>}><Gallery stop={stop} viewVersion={viewVersion} entered={entered} playing={playing} onStop={navigate} onTrack={index=>{const track=tracks[index];if(track){navigate(seasons.findIndex(s=>s.id===track.season)+1);selectTrack(track);}}} onWalk={()=>setRoaming(true)}/></Suspense>
      <div className="explore-label"><span className="eyebrow"><span/> VIVALDI · LE QUATTRO STAGIONI</span><h1>{roaming?'Jelajah bebas':stop===0?'Antonio Vivaldi':seasons[stop-1]?.italian||'Bottega Vivaldi'}</h1><p>{roaming?'Temukan karya, dengarkan kisahnya.':stop===0?'Empat musim. Dua puluh rekaman. Satu perjalanan.':stop===shopStop?'Kenangan dari Le quattro stagioni.':seasons[stop-1]?.label||''}</p></div>
      <div className="walk-instructions"><span className="key-cluster"><kbd>W</kbd><span><kbd>A</kbd><kbd>S</kbd><kbd>D</kbd></span></span><span>Berjalan di dalam museum<small>Seret untuk melihat · Shift untuk lebih cepat</small></span></div>
      {entered&&!roaming&&stop===0&&<button className="shop-hotspot" onClick={()=>navigate(shopStop)}><ShoppingBag size={18}/><span>Toko suvenir<small>Mampir sebentar</small></span><ArrowUpRight size={17}/></button>}
      {entered&&!roaming&&stop>0&&stop<=seasons.length&&<SeasonCard seasonIndex={stop-1} current={current} playing={playing} onSelect={chooseTrack} onBrowse={()=>browseSeason(seasons[stop-1].id)}/>}

      <div className="scene-bottom"><span className="location-label"><span/> ARS SONORA <span className="divider">/</span> {stop.toString().padStart(2,'0')}—04</span><div className="scene-tools">{entered&&<><span className="drag-hint">WASD berjalan · Seret melihat</span><button aria-label="Kembali ke pintu masuk museum" onClick={()=>{navigate(0);}} title="Sudut awal"><RotateCcw size={17}/></button></>}<button onClick={()=>void toggleFullscreen()} aria-label={fullscreen?'Keluar layar penuh':'Buka layar penuh'} title="Layar penuh">{fullscreen?<Minimize size={17}/>:<Maximize size={17}/>}</button><button onClick={()=>openPanel('about')} aria-label="Panduan galeri"><CircleHelp size={18}/></button></div></div>
    </main>
    <nav className="room-navigation" id="room-navigation" aria-label="Pilih ruang galeri"><div className="journey-label"><ArrowDown size={15}/><span>TEMUKAN<br/>RUANGMU</span></div><div className="room-buttons">{stops.map((name,i)=><button key={name} className={stop===i?'selected':''} aria-current={stop===i?'location':undefined} onClick={()=>navigate(i)}><span className="room-number">0{i}</span><span>{name}</span>{i===shopStop?<ShoppingBag size={16}/>:<ArrowUpRight size={16}/>}</button>)}</div><div className="room-arrows"><button aria-label="Ruang sebelumnya" onClick={()=>navigate((stop+stops.length-1)%stops.length)}><ChevronLeft size={17}/></button><button aria-label="Ruang berikutnya" onClick={()=>navigate((stop+1)%stops.length)}><ChevronRight size={17}/></button></div></nav>
    <section className="music-player" aria-label="Pemutar musik">
      <button className={`now-art ${playing?'record-spinning':''}`} onClick={()=>openPanel('collection')} aria-label="Lihat koleksi musik"><TrackArtwork track={current} small/></button>
      <div className="now-info"><span className="now-label">{loading?'MENYIAPKAN AUDIO…':playing?'SEDANG DIPUTAR':'SIAP DIDENGARKAN'}</span><button onClick={()=>openPanel('collection')}>{current.title}</button><small>{current.artist}<span> · {current.genre}</span></small></div>
      <div className="playback"><button className={`icon-button optional-control ${shuffle?'is-on':''}`} aria-pressed={shuffle} onClick={()=>setShuffle(!shuffle)} aria-label="Acak lagu"><Shuffle size={16}/></button><button className="icon-button" onClick={()=>nextTrack(-1)} aria-label="Lagu sebelumnya"><SkipBack size={18}/></button><button className="play-button" onClick={togglePlay} aria-label={playing?'Jeda musik':'Putar musik'} aria-busy={loading}>{loading?<span className="loading-ring"/>:playing?<Pause size={19} fill="currentColor"/>:<Play size={19} fill="currentColor"/>}</button><button className="icon-button" onClick={()=>nextTrack(1)} aria-label="Lagu berikutnya"><SkipForward size={18}/></button><button className={`icon-button optional-control ${repeat?'is-on':''}`} aria-pressed={repeat} onClick={()=>setRepeat(!repeat)} aria-label="Ulangi lagu"><Repeat size={16}/></button></div>
      <div className="timeline"><span>{timeLabel(elapsed)}</span><input type="range" min="0" max={duration||1} step=".1" value={Math.min(elapsed,duration||1)} aria-label="Posisi pemutaran" disabled={!duration} onChange={e=>{if(audio.current){audio.current.currentTime=Number(e.target.value);setElapsed(Number(e.target.value));}}} style={{'--progress':`${duration?elapsed/duration*100:0}%`} as React.CSSProperties}/><span>{timeLabel(duration)}</span></div>
      <div className="volume"><button className="icon-button" aria-label={muted?'Aktifkan suara':'Bisukan suara'} onClick={()=>{if(audio.current)audio.current.muted=!muted;setMuted(!muted);}}>{muted||volume===0?<VolumeX size={18}/>:<Volume2 size={18}/>}</button><input type="range" min="0" max="1" step=".01" value={muted?0:volume} aria-label="Volume musik" onChange={e=>{const v=Number(e.target.value);setVolume(v);setMuted(false);if(audio.current){audio.current.volume=v;audio.current.muted=false;}}}/></div>
      <button className="player-collection" onClick={()=>openPanel('collection')} aria-label="Buka daftar lagu"><Music2 size={19}/><span>KOLEKSI</span></button>
      <audio ref={audio} preload="none" onLoadedMetadata={()=>{if(audio.current)setDuration(audio.current.duration);}} onTimeUpdate={()=>{if(audio.current)setElapsed(audio.current.currentTime);}} onPlay={()=>{setPlaying(true);setLoading(false);}} onPause={()=>{setPlaying(false);setLoading(false);}} onWaiting={()=>setLoading(true)} onCanPlay={()=>setLoading(false)} onEnded={()=>{if(repeat){if(audio.current)audio.current.currentTime=0;void playAudio();}else nextTrack(1);}} onError={()=>{setLoading(false);setPlaying(false);setAudioError('Lagu tidak bisa dimuat. Coba lagi atau pilih lagu lain.');}}/>
    </section>
    <footer className="site-footer"><span>ARS SONORA © 2026</span><span><span className="live-dot"/> ARS LONGA, VITA BREVIS.</span><button onClick={()=>openPanel('about')}>Kredit & lisensi <ArrowUpRight size={11}/></button></footer>
    {audioError&&<div className="audio-error" role="alert"><span>{audioError}</span><button onClick={()=>{if(audio.current&&!audio.current.getAttribute('src'))audio.current.src=current.src;void playAudio();}}>Coba lagi</button><button aria-label="Tutup pesan error" onClick={()=>setAudioError('')}><X size={15}/></button></div>}
    {notice&&!panel&&<div className="toast" role="status"><Check size={17}/>{notice}</div>}
    <dialog ref={dialog} aria-label={panel==='collection'?'Koleksi musik':panel==='about'?'Panduan dan kredit galeri':panel==='cart'?'Tas belanja suvenir':'Toko suvenir'} className={`drawer drawer-${panel}`} onCancel={()=>setPanel(null)} onClose={()=>setPanel(null)} onClick={e=>{if(e.target===e.currentTarget)setPanel(null);}}>
      <div className="drawer-surface"><div className="drawer-top"><span className="eyebrow">ARS SONORA / {panel==='collection'?'THE COLLECTION':panel==='about'?'THE SPACE':'THE SOUVENIR SHOP'}</span><button className="close-button" onClick={()=>setPanel(null)} aria-label="Tutup panel"><X size={21}/></button></div>
        {panel==='collection'&&<SeasonCollection library={library} current={current} playing={playing} initialSeason={collectionSeason} onSelect={chooseTrack} onUpload={uploadMusic} uploadError={uploadError} onCredits={()=>openPanel('about')}/>}
        {panel==='shop'&&<><div className="drawer-heading"><span className="section-kicker">OBJECTS FOR THE EVERYDAY</span><h2>Kenangan,<br/>dalam bentuk lain.</h2><p>Sesuatu yang kecil. Cerita yang tinggal.</p></div><div className="demo-note">SIMULASI TOKO <span>Semua pembelian menggunakan saldo demo.</span></div><div className="product-grid">{products.map(product=><article className="product-card" key={product.id}><ProductArt product={product}/><span className="product-type">{product.type}</span><h3>{product.name}</h3><p>{product.detail}</p><div className="product-purchase"><strong>{rupiah(product.price)}</strong><button onClick={()=>addToCart(product)} aria-label={`Tambahkan ${product.name} ke tas`} disabled={(cart[product.id]||0)>=20}>{(cart[product.id]||0)>=20?<Check size={17}/>:<Plus size={18}/>}</button></div></article>)}</div><button className="solid-button shop-bag" onClick={()=>openPanel('cart')}><ShoppingBag size={18}/>Lihat tas belanja <span>{count} barang <ArrowRight size={18}/></span></button><p className="shop-footnote">Objek dan harga merupakan contoh. Tidak ada transaksi uang asli.</p></>}
        {panel==='cart'&&(order?<div className="order-success"><span className="success-mark"><Check size={33}/></span><span className="section-kicker">SIMULASI BERHASIL</span><h2>Sepotong ruang,<br/>untukmu.</h2><p>Pesanan demo Anda sudah tercatat.<br/>Tidak ada uang yang ditagih atau barang dikirim.</p><dl><div><dt>Nomor pesanan</dt><dd>{order.id}</dd></div><div><dt>Total simulasi</dt><dd>{rupiah(order.total)}</dd></div><div><dt>Pembayaran</dt><dd>Saldo demo</dd></div></dl><button className="solid-button" onClick={()=>{setPanel(null);setStop(0);}}>Kembali menikmati galeri <ArrowRight size={18}/></button></div>:<><div className="drawer-heading"><span className="section-kicker">SOUND, TO GO.</span><h2>Tas belanja<span className="heading-count">{count}</span></h2><p>Pilihan kecil dari ruang yang Anda kunjungi.</p></div>{count?<><div className="cart-items">{products.filter(p=>cart[p.id]).map(product=><article className="cart-item" key={product.id}><ProductArt product={product}/><div><h3>{product.name}</h3><small>{product.type}</small><strong>{rupiah(product.price)}</strong><div className="quantity-control"><button aria-label={`Kurangi ${product.name}`} disabled={checkingOut} onClick={()=>setCart(old=>changeQuantity(old,product.id,-1))}><Minus size={14}/></button><output>{cart[product.id]}</output><button aria-label={`Tambah ${product.name}`} disabled={checkingOut||cart[product.id]>=20} onClick={()=>setCart(old=>changeQuantity(old,product.id,1))}><Plus size={14}/></button><button className="remove-item" disabled={checkingOut} onClick={()=>setCart(old=>changeQuantity(old,product.id,-20))}>Hapus</button></div></div></article>)}</div><div className="checkout-summary"><div><span>Subtotal</span><strong>{rupiah(cartTotal(cart))}</strong></div><div><span>Pengiriman</span><span>Tidak diperlukan (demo)</span></div><div className="checkout-total"><span>Total simulasi</span><strong>{rupiah(cartTotal(cart))}</strong></div><div className="payment-method"><span className="payment-selected"><Check size={12}/></span><span>Saldo demo<small>Pembayaran virtual untuk mencoba pengalaman.</small></span><span>DEMO</span></div><button className="solid-button" disabled={checkingOut} onClick={checkout}>{checkingOut?<><span className="loading-ring"/>Memproses simulasi…</>:<>Selesaikan pembelian demo <ArrowUpRight size={19}/></>}</button><p className="shop-footnote">Tidak memerlukan data pribadi atau pembayaran asli.</p></div></>:<div className="empty-cart"><ShoppingBag size={39} strokeWidth={1}/><h3>Masih ada ruang di tas Anda.</h3><p>Mampir ke toko dan temukan suvenir favorit.</p><button className="solid-button" onClick={()=>openPanel('shop')}>Jelajahi suvenir <ArrowRight size={17}/></button></div>}</>)}
        {panel==='about'&&<VivaldiAbout onCollection={()=>openPanel('collection')}/>}
      </div>
      {notice&&<div className="toast" role="status"><Check size={17}/>{notice}</div>}
    </dialog>
    <InitialAudio audio={audio}/>
  </div>;
}
function InitialAudio({audio}:{audio:React.RefObject<HTMLAudioElement|null>}){useEffect(()=>{if(audio.current&&!audio.current.getAttribute('src')){audio.current.src=tracks[0].src;audio.current.volume=.65;}},[audio]);return null;}
