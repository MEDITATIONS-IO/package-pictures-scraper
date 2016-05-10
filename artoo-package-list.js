artoo.scrape('figure', {
  title: {sel: 'span[id*="Title2"]'},
  caption: {sel: 'span[id*="CpationShort"]'},
  imageUrl: {sel: 'img[id*="I_img"]', attr: 'src'},
  count: {
    sel: 'span[id*="MediaCount"]',
    method: function($) {
      var numberPattern = /\d+/g;
      return parseInt($(this).text().match( numberPattern )[0])
    }
  },
  url: {sel: '.Hyperlink a', attr: 'href'}
});
