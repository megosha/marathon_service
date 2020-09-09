
(function(){$(".modalWindow").on("hidden.bs.modal",function(a){a=$(a.target).find("iframe");/youtu/.test(a.attr("src"))?a[0].contentWindow.postMessage('{"event":"command","func":"pauseVideo","args":""}',"*"):/vimeo/.test(a.attr("src"))&&(new Vimeo.Player(a)).pause()})})();
