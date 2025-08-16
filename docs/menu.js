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

      function close(){ items.classList.remove('open'); toggle.setAttribute('aria-expanded','false') }
      function open(){ items.classList.add('open'); toggle.setAttribute('aria-expanded','true') }
      function toggleOpen(){ items.classList.contains('open') ? close() : open() }

      toggle.addEventListener('click', function(){ toggleOpen() })

      // 點擊外部時關閉
      document.addEventListener('click', function(e){
        if(!items.classList.contains('open')) return
        if(h.contains(e.target)) return
        close()
      })

      // ESC 關閉
      document.addEventListener('keydown', function(e){
        if(e.key === 'Escape') close()
      })
    })
  })
})()


