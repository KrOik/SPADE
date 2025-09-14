Build your first function
构建你的第一个函数

Install the Netlify CLI  安装 Netlify CLI
Run the commands in your terminal from your linked repository.
从已链接的存储库中在你的终端运行命令。

npm install netlify-cli -g

Create a new function  创建新函数
The CLI will prompt you to pick a template for your function.
CLI 将提示您选择函数模板。

netlify functions:create

Push to Git to deploy!
推送到 Git 以部署！
When done, you can invoke your function at /.netlify/functions/FUNCTION-NAME, relative to the base URL of your deployed project.
完成后，您可以在 /.netlify/functions/FUNCTION-NAME 处调用您的函数，相对于已部署项目的基 URL。

帮助文档：
https://docs.netlify.com/functions/overview/?_gl=1%2a1belug5%2a_gcl_au%2aMjEyNzQ5MTczNi4xNzQzNTEyNTE1
https://docs.netlify.com/functions/get-started/?fn-language=ts
https://docs.netlify.com/functions/get-started/?fn-language=js
https://docs.netlify.com/functions/get-started/?fn-language=go