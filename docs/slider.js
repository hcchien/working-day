;(function(){
  function ready(fn){
    if(document.readyState==='loading'){
      document.addEventListener('DOMContentLoaded', fn)
    } else { fn() }
  }

  function clamp(n, min, max){ return Math.max(min, Math.min(max, n)) }

  ready(function(){
    var slideshow = document.querySelector('.slideshow')
    if(!slideshow) return
    var slides = Array.prototype.slice.call(slideshow.querySelectorAll('.slide'))
    var dots = Array.prototype.slice.call(document.querySelectorAll('.sequence .dot'))
    var prev = slideshow.querySelector('.prev')
    var next = slideshow.querySelector('.next')
    var idx = slides.findIndex(function(s){ return s.classList.contains('active') })
    if(idx < 0) idx = 0

    function setActive(i){
      // 循環切換
      if(slides.length === 0) return
      if(i < 0) i = slides.length - 1
      if(i >= slides.length) i = 0
      slides.forEach(function(s,j){ s.classList.toggle('active', j===i) })
      dots.forEach(function(d,j){
        var img = d.querySelector('img') || d
        img.src = j===i ? 'image_blackdot.png' : 'image_greydot.png'
        d.setAttribute('aria-selected', j===i ? 'true' : 'false')
        d.setAttribute('tabindex', j===i ? '0' : '-1')
      })
      idx = i
    }

    // 正確方向：prev 往左（上一張），next 往右（下一張）
    if(prev) prev.addEventListener('click', function(){ setActive(idx-1) })
    if(next) next.addEventListener('click', function(){ setActive(idx+1) })
    dots.forEach(function(d){
      d.setAttribute('role', 'tab')
      d.setAttribute('aria-controls', 'slide-'+d.dataset.idx)
      d.addEventListener('click', function(){ setActive(parseInt(d.dataset.idx,10)) })
      d.addEventListener('keydown', function(e){
        if(e.key === 'Enter' || e.key === ' ') { e.preventDefault(); setActive(parseInt(d.dataset.idx,10)) }
      })
    })

    // Swipe 支援
    var startX = null
    slideshow.addEventListener('touchstart', function(e){
      if(e.touches && e.touches[0]) startX = e.touches[0].clientX
    }, { passive: true })
    slideshow.addEventListener('touchmove', function(e){}, { passive: true })
    slideshow.addEventListener('touchend', function(e){
      if(startX == null) return
      var endX = (e.changedTouches && e.changedTouches[0]) ? e.changedTouches[0].clientX : startX
      var dx = endX - startX
      if(Math.abs(dx) > 40){
        if(dx < 0) setActive(idx+1)  // 往左滑，下一張
        else setActive(idx-1)        // 往右滑，上一張
      }
      startX = null
    })

    // 鍵盤左右鍵控制（聚焦於輪播時）
    slideshow.setAttribute('tabindex','0')
    slideshow.setAttribute('role','region')
    slideshow.setAttribute('aria-label','Image slideshow')
    slideshow.addEventListener('keydown', function(e){
      if(e.key === 'ArrowLeft') setActive(idx-1)
      if(e.key === 'ArrowRight') setActive(idx+1)
    })
  })
})()


