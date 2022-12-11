var updatesBtns=document.getElementsByClassName('update-cart')
for(i=0;i<updatesBtns.length;i++){
    updatesBtns[i].addEventListener('click',function(){
        var productId=this.dataset.product
        var action=this.dataset.action
        console.log('productId:',productId,'action:',action)
        
        console.log('User:',user)
        if(user=='AnonymousUser'){
            // console.log('User is not authenticated')
            addCookieItem(productId,action);
        }
        else{
               updateUserOrder(productId,action) 
        }

    })
}

function addCookieItem(productId,action){
    console.log('not logged in...');

    if(action=='add'){
        if(cart[productId]==undefined){
            cart[productId]={'quantity':1}
        }
        else{
            cart[productId]['quantity']+=1
        }
    }
    if(action=='remove'){
        cart[productId]['quantity']-=1;

        if(cart[productId]['quantity']<=0){
            console.log('Item should be deleted')
            delete cart[productId];
        }
    }
      console.log('Cart:',cart)
      document.cookie='cart='+JSON.stringify(cart) + ";domain;path=/"
      location.reload()
}


function updateUserOrder(productId,action){
    console.log('user is authenticated,sending data...')
    var url='/update_item/'
    fetch(url,{
        method:'POST',
        headers:{'Content-Type':'application/json','X-CSRFToken':csrftoken,},
        body:JSON.stringify({'productID':productId,'action':action})
    })
    .then((response)=>{return response.json()})
    .then((data)=>{
        console.log('Data is :',data);
        location.reload();

    })
}