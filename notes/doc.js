(function(){
  var input=document.getElementById('q');
  if(!input)return;
  var cards=[].slice.call(document.querySelectorAll('.card'));
  var chips=[].slice.call(document.querySelectorAll('.chip'));
  var empty=document.getElementById('empty');
  var group='all';
  function apply(){
    var q=input.value.trim().toLowerCase();
    var shown=0;
    cards.forEach(function(c){
      var ok=(group==='all'||c.dataset.group===group)&&(!q||c.dataset.search.indexOf(q)>-1);
      c.style.display=ok?'':'none';
      if(ok)shown++;
    });
    if(empty)empty.style.display=shown?'none':'';
  }
  input.addEventListener('input',apply);
  chips.forEach(function(ch){
    ch.addEventListener('click',function(){
      chips.forEach(function(x){x.classList.remove('on')});
      ch.classList.add('on');group=ch.dataset.group;apply();
    });
  });
})();
