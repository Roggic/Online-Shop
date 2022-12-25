document.addEventListener("DOMContentLoaded", function() {
  changeTotal();
});

var check = false;

// Итого по продукту
function changeVal(el) {
  var qt = parseFloat(el.parent().parent().children(".qt").val());
  console.log(qt);
  var price = parseFloat(el.parent().parent().parent().parent().children(".price").html());

  var eq = Math.round(price * qt * 100) / 100;

  el.parent().parent().parent().parent().children(".full-price").html( eq + " руб." );

  changeTotal();
}

// Всего по заказу
function changeTotal() {

  var price = 0;

  $(".full-price").each(function(index){
    price += parseFloat($(".full-price").eq(index).html());
  });

  price = Math.round(price * 100) / 100;
  var shipping = parseFloat($(".shipping").html());
  var fullPrice = Math.round((price + shipping) * 100) / 100;

  if(price == 0) {
    fullPrice = 0;
  }

  $(".subtotal").html(price + " руб.");
  $(".total").html(fullPrice + " руб.");
}

$(document).ready(function(){

  // Удалить продукт
  $(".remove").click(function(){
    var el = $(this);
    el.parent().parent().addClass("removed");
    el.parent().parent().children(".full-price").removeClass("full-price");
    console.log(el.parent().children(".cart-delete").children())
    el.parent().children(".cart-delete").children().prop('checked', true);
    window.setTimeout(
      function(){
        el.parent().parent().slideUp('fast', function() {
          el.parent().parent().hide();
          if($(".content").length == 0) {
            if(check) {
              $("#cart").html("<h1>The shop does not function, yet!</h1><p>If you liked my shopping cart, please take a second and heart this Pen on <a href='https://codepen.io/ziga-miklic/pen/xhpob'>CodePen</a>. Thank you!</p>");
            } else {
              $("#cart").html("<h1>No products!</h1>");
            }
          }
          changeTotal();
        });
      }, 200);
  });

  // Увеличить количество
  $(".qt-plus").click(function(){
    $(this).parent().children(".qt").html(parseInt($(this).parent().children(".qt").html()) + 1);

    $(this).parent().children(".full-price").addClass("added");

    var el = $(this);
    window.setTimeout(function(){el.parent().children(".full-price").removeClass("added"); changeVal(el);}, 150);
  });

  // Уменьшить количество
  $(".qt-minus").click(function(){

    child = $(this).parent().children(".qt");

    if(parseInt(child.html()) > 1) {
      child.html(parseInt(child.html()) - 1);
    }

    $(this).parent().children(".full-price").addClass("minused");

    var el = $(this);
    window.setTimeout(function(){el.parent().children(".full-price").removeClass("minused"); changeVal(el);}, 150);
  });

  window.setTimeout(function(){$(".is-open").removeClass("is-open")}, 1200);

    $('.btn-plus, .btn-minus').on('click', function(e) {
      const isNegative = $(e.target).closest('.btn-minus').is('.btn-minus');
      const input = $(e.target).closest('.input-group').find('input');
      if (input.is('input')) {
        input[0][isNegative ? 'stepDown' : 'stepUp']()
      }
    var el = $(this);
    changeVal(el);
})
//  $(".btn").click(function(){
//    check = true;
//    $(".remove").click();
//  });
});