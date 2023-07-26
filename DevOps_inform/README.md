<h1>Здесь располагаются детали по настройке отдельных модулей проекта.</h1>
<ol>
<h2><li>nginx-push-stream-module (Linux Ubuntu 22.04 LTS)</li></h2>
<div style="text-align: justify;">
<ol style="font-size: 16px">
<li>Для работы этого модуля необходимо его установить по инструкции по ссылке: <a>https://www.nginx.com/resources/wiki/modules/push_stream/</a>
<li>Данный модуль является статическим, поэтому для его установки будет необходимо перекомпилировать nginx.</li>
<li>При сборке nginx необходимо указывать модули, которые будут включены в него, но т.к. эти модули уже есть в стандартно установленным через <b><i>sudo apt install nginx</i></b> приложении, то их необходимо скопировать и добавить к устанавливаемому модулю (сами модули есть в папке nginx_conf в репозитории).</li>
<li>После чего необходимо установить этот модуль по инструкции по ссылке: <a>https://firstvds.ru/technology/dobavlenie-moduley-nginx-v-linux-debianubuntucentosalmalinux></a></li>
<li>Далее необходимо проверить правильность установленного модуля, проверив его с помощью конфига, находящегося в something_directory/nginx-pish-stream-module/misc/nginx.conf, однако данное сообщение выдаст ошибку на команду <b><i>poll</i></b>, поэтому её необходимо заменить на <b><i>epoll</i></b>, что указано в ответе автора данного модуля: <a>https://github.com/wandenberg/nginx-push-stream-module/issues/257#issuecomment-292965008></a></li>
<li>В результате проведённой замены тест будет пройден и модуль настроен.</li>
</ol>
</div>
<h2><li>Centrifugo (v.3.1.1)</li></h2>
<div style="text-align: justify;">
<ol style="font-size: 16px">
<li>Для работы этого модуля необходимо его установить по инструкции по ссылке: <a>https://github.com/centrifugal/centrifugo/releases/tag/v3.1.1</a></li>
<li>Нужно создать конфиг для дальнейшей его настройки и управлением с помощью команды <i><b>./centrifugo genconfig</i></b></li>
<li>После этого необходимо в settings.py проекта добавить <i><b>CENTRIFUGO_API_KEY</i></b>, <i><b>CENTRIFUGO_SECRET_KEY</i></b>, <i><b>CENTRIFUGO_ADDRESS</i></b> значения которых нужно взять из сгенерированного файла.</li>
<li> Пример остальной настройки (настройка JS в файле <i><b>index.html</i></b>, а настройках обработки запросов в <i><b>views.py</i></b>) можно найти в файлах проекта.</li>
</ol>
</div>
</ol>