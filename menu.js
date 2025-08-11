;(function(){
  function ready(fn){
    if(document.readyState==='loading'){
      document.addEventListener('DOMContentLoaded', fn)
    } else { fn() }
  }

  ready(function(){
    var headers = document.querySelectorAll('.uh')
    headers.forEach(function(h){
      var toggle = h.querySelector('.menu-toggle')
      var items = h.querySelector('.menu-items')
      if(!toggle || !items) return
      toggle.addEventListener('click', function(){
        var open = items.classList.toggle('open')
        toggle.setAttribute('aria-expanded', open ? 'true' : 'false')
      })
    })
  })
})()


