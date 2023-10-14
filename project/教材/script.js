const starbuttons  = [document.getElementById("starbutton_1"),
document.getElementById("starbutton_2"),
document.getElementById("starbutton_3"),
document.getElementById("starbutton_4"),
document.getElementById("starbutton_5")]
const comment = document.getElementById("comment");
const submitbutton = document.getElementById("submitbutton");
var rate = 0;
submitbutton.disabled=true;
function star_update(n){
    rate = n;
    for (var i=1;i<=5;i++){
        submitbutton.disabled=false;
        if (i<=rate){
            starbuttons[i-1].style.color = "#ffcd00";
        } else {
            starbuttons[i-1].style.color = "gray";
        }
    }

}
function test(){
    window.alert("理解度は「"+rate+"」、コメントは「"+comment.value+"」です");
}