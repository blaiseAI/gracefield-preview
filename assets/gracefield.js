// Gracefield preview interactions (vanilla, no dependencies)
(function(){
  // Expanding phone menu
  var toggle=document.querySelector('.menu-toggle');
  var panel=document.getElementById('site-nav');
  function setMenu(open){
    if(!toggle||!panel)return;
    toggle.setAttribute('aria-expanded',String(open));
    panel.classList.toggle('open',open);
    toggle.querySelector('.label').textContent=open?'Close':'More';
  }
  if(toggle){
    toggle.addEventListener('click',function(){setMenu(toggle.getAttribute('aria-expanded')!=='true')});
    document.addEventListener('keydown',function(e){
      if(e.key==='Escape'&&toggle.getAttribute('aria-expanded')==='true'){setMenu(false);toggle.focus()}
    });
    panel.addEventListener('click',function(e){if(e.target.closest('a'))setMenu(false)});
  }

  // Local details panel (hero-only preview)
  var dlg=document.getElementById('menu-details');
  document.querySelectorAll('[data-open-details]').forEach(function(b){
    b.addEventListener('click',function(e){if(dlg&&dlg.showModal){e.preventDefault();dlg.showModal()}});
  });
  if(dlg){
    dlg.querySelector('.close').addEventListener('click',function(){dlg.close()});
    dlg.addEventListener('click',function(e){if(e.target===dlg)dlg.close()});
  }

  // Floating call bar (desktop) shows whenever the page's own call button is off screen; phones show it always (CSS)
  var bar=document.querySelector('.callbar');
  var heroCta=document.querySelector('[data-callbar-anchor]');
  if(bar&&heroCta&&'IntersectionObserver'in window){
    new IntersectionObserver(function(en){bar.classList.toggle('show',!en[0].isIntersecting)}).observe(heroCta);
  }

  // Full menu: highlight the chip for the section in view
  var chips=document.querySelectorAll('.cat-bar a');
  if(chips.length&&'IntersectionObserver'in window){
    var strip=document.querySelector('.cat-bar .cat-chips');
    var io=new IntersectionObserver(function(entries){
      entries.forEach(function(en){
        if(!en.isIntersecting)return;
        chips.forEach(function(a){
          var on=a.getAttribute('href')==='#'+en.target.id;
          if(on){a.setAttribute('aria-current','true');strip.scrollTo({left:a.parentElement.offsetLeft-16,behavior:'smooth'})}
          else a.removeAttribute('aria-current');
        });
      });
    },{rootMargin:'-30% 0px -60% 0px'});
    document.querySelectorAll('.cat-section').forEach(function(sec){io.observe(sec)});
  }

  // Open / closed status, in Edmonton time. PLACEHOLDER HOURS: confirm with Gracefield.
  // Index 0 = Sunday. [open, close] in 24h hours, or null when closed all day.
  var HOURS=[[11,21],null,[11,21],[11,21],[11,21],[11,21],[11,21]];
  var DAYS=['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
  function fmt(h){var s=h%12||12;return s+(h<12?' am':' pm')}
  function statusText(){
    var p={};
    new Intl.DateTimeFormat('en-CA',{timeZone:'America/Edmonton',weekday:'short',hour:'numeric',minute:'numeric',hourCycle:'h23'})
      .formatToParts(new Date()).forEach(function(x){p[x.type]=x.value});
    var day=DAYS.indexOf(p.weekday), now=+p.hour+(+p.minute)/60;
    if(day<0)return null;
    var today=HOURS[day];
    if(today&&now>=today[0]&&now<today[1])return {open:true,text:'Open now · until '+fmt(today[1])};
    if(today&&now<today[0])return {open:false,text:'Closed · opens '+fmt(today[0])+' today'};
    for(var i=1;i<=7;i++){
      var d=(day+i)%7, h=HOURS[d];
      if(h)return {open:false,text:'Closed · opens '+(i===1?'tomorrow':DAYS[d])+' '+fmt(h[0])};
    }
    return null;
  }
  try{
    var st=statusText();
    if(st)document.querySelectorAll('[data-open-status]').forEach(function(el){
      el.textContent=st.text;
      el.classList.add(st.open?'is-open':'is-closed');
      el.hidden=false;
    });
  }catch(e){/* leave status hidden */}
})();
