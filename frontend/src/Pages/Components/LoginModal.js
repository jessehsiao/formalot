import '../../css/LoginModal.css';
import React from "react";
import ReactDom from "react-dom";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Homepage } from "../Homepage";

function LoginModal( {closeModal}){
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const navigate = useNavigate();

    // 登入
    const callLoginApi = async (e) => {
        e.preventDefault();
        const result = await fetch("http://127.0.0.1:5000/Login", {
            method: "POST",
            body: JSON.stringify({
                email: email,
                password: password,
            }),
        });
        let resJson = await result.json();
        if (resJson.access_token){
            localStorage.setItem('jwt', resJson.access_token);
            localStorage.setItem('refresh_token', resJson.refresh_token);
            console.log("Login Success");
            console.log(resJson.access_token);
            alert("Login Success");
            window.location.reload();
            navigate(<Homepage/>);
            
        }else{
            console.log(resJson);
            alert(resJson.message);
        };
    };


    // 登出
    // const calllogout = async (e) => {
    //     e.preventDefault();
    //     localStorage.removeItem('jwt');
    //     console.log("Logout Success");
    //     alert("Logout Success");
   
    // };

    // 更新使用者資訊
    // const calluserupdate = async (e) => {
    //     e.preventDefault();
    //     const getprotected = await fetch('http://127.0.0.1:5000/UserUpdate',{
    //         method: 'PUT',
    //         headers: {
    //           Authorization: `Bearer ${localStorage.getItem('jwt')}`,
    //         },
    //         body: JSON.stringify({
    //             first_name: "testupdate",
    //             last_name : "",
    //             password : "",
    //             password2 : "",
    //         }),
    //     });
    //     const resdata = await getprotected.json();
    //     console.log(resdata);
    //     alert(resdata.message);
   
    // };

    // 忘記密碼
    // const [newpsw, setNewPsw] = useState("");
    // const [newpsw2, setNewPsw2] = useState("");
    // const [code, setCode] = useState("");
    // const callforgetpasswordApi = async (e) => {
    //     e.preventDefault();
    //     const getprotected = await fetch('http://127.0.0.1:5000/ForgetPsw',{
    //         method: 'PUT',
    //         body: JSON.stringify({
    //             email: email,
    //             password : newpsw,
    //             password2 : newpsw2,
    //             code: code,
    //             session_code: sessionStorage.getItem('code')
    //         }),
    //     });
    //     const resdata = await getprotected.json();
    //     console.log(resdata);
    //     alert(resdata.message);

    // };


    // 傳送驗證碼 api
    // const callemailApi = async (e) => {
    //     e.preventDefault();
    //     const result = await fetch("http://127.0.0.1:5000/Email?condition=forget_psw", {
    //         method: "POST",
    //         body: JSON.stringify({
    //             email: email
    //         }),
    //     });
    //     let resJson = await result.json();
    //     console.log(resJson);
    //     alert(resJson.message);
    //     sessionStorage.setItem('code', resJson.code);
    // };

    // validation
        let errors = {};
      
        // if (!email.trim()) {
        //   errors.username = 'Username required';
        // }
        // else if (!/^[A-Za-z]+/.test(values.name.trim())) {
        //   errors.name = 'Enter a valid name';
        // }
      
        if (!/\S+@\S+\.edu+\.tw+/.test(email)) {
          errors.email = '請使用大專院校信箱！';
        } 
        // else if (!/\S+@\S+\.\S+/.test(email)) {
        //     errors.email = '信箱格式錯誤';
        // }


        if (!password) {
          errors.password = '請輸入密碼';
        } 
        // else if (values.password.length < 6) {
        //   errors.password = 'Password needs to be 6 characters or more';
        // }
      
        // if (!values.password2) {
        //   errors.password2 = 'Password is required';
        // } else if (values.password2 !== values.password) {
        //   errors.password2 = 'Passwords do not match';
        // }
      

        return ReactDom.createPortal(
            <div className='modalBackground'>
                <div className="modalContainer">
                    <button onClick={() => closeModal(false)} className="titleCloseBtn">X</button>
                        <div align="center" className="title">
                            <h2>登入</h2>
                        </div>

                        <div className='login-form-input'>
                            {/* <label className='form-label'>帳號</label> */}
                            <input placeholder="電子郵件" className="inputbar" value={email} onChange={(e) => setEmail(e.target.value)}></input>
                            {errors.email && <font>{errors.email}</font>}
                        </div>
                        <p></p>
                        <div className='login-form-input'>
                            {/* <label className='form-label'>密碼</label> */}
                            <input type="password" placeholder="密碼" className="inputbar" value={password} onChange={(e) => setPassword(e.target.value)}></input>
                            {errors.password && <font>{errors.password}</font>}
                        </div>

                        <div align="center">
                            <button className="submit" onClick={callLoginApi}>登入</button><br/>
                            <button className="forget-password" onClick={() => {window.location.href='ForgetPassword'}}>忘記密碼?</button>
                        </div>                                
                        <div className="login-button" align="center">
                            <button className="create-account-button" onClick={() => {window.location.href='register'}}>建立新帳號</button>
                            {/* <button className="forget-password">忘記密碼？</button><br/> */}
                        </div>
                </div>
            </div>,
            document.getElementById("portal")
        )
}
export { LoginModal };