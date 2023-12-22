const formOpenBtn=document.querySelector("#form-open"),
  home=document.querySelector(".home"),
  formContainer=document.querySelector(".form_container"),
  formCloseBtn=document.querySelector(".form_close"),
  signupBtn=document.querySelector("#signup"),
  loginBtn=document.querySelector("#login"),
  pwShowHide=document.querySelectorAll(".pw_hide");

  formOpenBtn.addEventListener("click", () => home.classList.add("show"))
  formCloseBtn.addEventListener("click", () => home.classList.remove("show"))

  pwShowHide.forEach((icon) =>{
    icon.addEventListener("click", ()=>{
      let getPwInput=icon.parentElement.querySelector("input");
      if(getPwInput.type==="password"){
        getPwInput.type="text";
        icon.classList.replace("uil-eye-slash", "uil-eye");
      }else{
        getPwInput.type="password";
        icon.classList.replace("uil-eye", "uil-eye-slash");
      }
    });
 
  });

  signupBtn.addEventListener("click", (e) => {
    e.preventDefault();
    formContainer.classList.add("active");
  });

  loginBtn.addEventListener("click", (e) => {
    e.preventDefault();
    formContainer.classList.remove("active");
  })

  function handleFormSubmission(formId, endpoint) {
    const form = document.getElementById(formId);
  
    form.addEventListener("submit", function (event) {
      event.preventDefault();
      console.log("Form submitted");
  
      const email = form.querySelector("input[type='email']").value;
      const password = form.querySelector("input[type='password']").value;
  
      console.log('Email:', email);
      console.log('Password:', password);
  
      const formData = new FormData();
      formData.append('email', email);
      formData.append('password', password);

      // Check if confirm_password field exists (for signup form)
      const confirm_password_field = form.querySelector("input[name='confirm_password']");
      if (confirm_password_field) {
      const confirm_password = confirm_password_field.value;
      console.log('Confirm Password:', confirm_password);
      formData.append('confirm_password', confirm_password);
    }

      console.log(formData);
  
      fetch(endpoint, {
        method: 'POST',
        body: formData
      }).then(response => {
        if (response.ok) {
          console.log('Form submitted successfully');
          return response.json();
        } else {
          console.error('Form submission failed');
          return response.json();
        }
      }).then(data => {
        console.log('Server response:', data);
      }).catch(error => {
        console.error('Fetch error:', error);
      });
    });
  }
  
  // Add an event listener for the "Login Now" button
  const loginButton = document.getElementById('loginButton');
  loginButton.addEventListener('click', function() {
    handleFormSubmission("loginForm", "/login");
  });

  // Add an event listener for the "Signup Now" button
const signupButton = document.getElementById('signupButton');
signupButton.addEventListener('click', function() {
  handleFormSubmission("signupForm", "/signup");
});