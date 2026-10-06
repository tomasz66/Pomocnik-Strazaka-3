const { chromium } = require('playwright');
(async()=>{
  const b=await chromium.launch(); const p=await b.newPage();
  await p.goto('file://'+process.argv[2]); await p.emulateMedia({media:'print'});
  // Dla każdej strony: największa czcionka, przy której wszystkie kolumny mieszczą się w kartce
  const sizes=await p.$$eval('section',secs=>secs.map(sec=>{
    let fs=9.5; const cols=sec.querySelector('.cols');
    const fits=()=>[...cols.children].every(c=>c.getBoundingClientRect().bottom<=sec.getBoundingClientRect().bottom-22);
    sec.style.fontSize=fs+'pt';
    while(!fits() && fs>4){ fs-=0.1; sec.style.fontSize=fs.toFixed(1)+'pt'; }
    return fs.toFixed(1);
  }));
  console.log('czcionka pt:',sizes.join(', '));
  await p.pdf({path:process.argv[3],width:'210mm',height:'297mm',printBackground:true,margin:{top:0,bottom:0,left:0,right:0}});
  await b.close();
})();
