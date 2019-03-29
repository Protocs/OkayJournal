# OkayJournal

OkayJournal — электронный дневник, открывающий возможности для учителей, учеников, родителей и школьной администрации.
## История создания
Идея проекта пришла к нам благодаря системе «Сетевой город», которой активно пользуются по всей стране. Мы решили попробовать самостоятельно построить такую систему, возможно внести какие-то собственные идеи в реализацию.

## Авторы
- [Protocs (Уткин Никита)](https://github.com/Protocs)
- [makeitokay (Васильев Андрей)](https://github.com/makeitokay)
- [nikitakosatka (Усатов Никита)](https://github.com/nikitakosatka)

## Реализация

### Вне системы
Вне основной системы есть три страницы:
-	/index – главная страница. На ней есть основная информация о ресурсе, кнопки входа и регистрации, поддержка;
-	/login – страница авторизации;
-	/register – страница отправки заявки на регистрацию новой школы.
### Система
В системе у каждого пользователя есть роль:
-	Ученик
-	Учитель
-	Родитель
-	Администратор школы
-	Администратор системы

Рассмотрим все основные возможности для каждой роли, а также страницы, которые доступны всем пользователям.

#### Все пользователи
-	/announcements – доска объявлений школы. Объявления публиковать могут только учителя и школьный администратор;
-	/messages – OkayJournal мессенджер. У каждого пользователя есть возможность вести переписку с любым другим пользователем, зарегистрированным в этой же школе;
-	/settings – настройки профиля. Можно сменить пароль и электронную почту;
#### Администратор школы
Администратор школы – тот, кто отправил заявку на регистрацию школы. Эта заявка приходит администратору системы, который решает, принимать ее или нет. Если да, то на почту, указанную при регистрации, приходит логин и пароль. Затем школьный администратор может начать пользоваться системой и заполнять свою школу.
-	/school_managing – меню настроек школы. На этой странице расположены все основные возможности школьного администратора;
-	/users – добавление новых пользователей: учителей, учеников и законных представителей (родителей).
-	/school_settings – настройка информации о школе: местоположение и т.д.;
-	/classes – страница с настройками классов. Можно добавлять новые классы и назначать им классного руководителя;
-	/subjects – страница с добавлением новых учебных предметов в школу;
-	/timetable – страница с составлением расписания на учебный год для определенного класса;
-	/lesson_times – страница с настройками расписания звонков в школе.
#### Администратор системы
-	/admin – страница, на которой отображаются все отправленные заявки на регистрацию школ. Можно либо принять, либо отклонить заявку.
#### Учитель
-	/journal – журнал с оценками для выбранного предмета, класса и четверти. Представлен в виде таблицы со всеми учениками в выбранном классе. Для удобства высчитывается средний балл для каждого ученика;
-	/grading – страница с выставлением оценок для выбранного предмета, класса, четверти и даты. Попасть на нее можно, нажав на таблицу на странице /journal;
Ученик и родитель
-	/diary – дневник. Можно выбрать неделю. Показываются все предметы на этой неделе, оценки, домашние задания. Родитель может выбирать ребенка, дневник которого он хочет посмотреть;
-	/reports – отчёты об оценках ученика за определенную четверть. Отображается количество оценок: пятерок, четверок, троек, двоек. Высчитывается средний балл по каждому предмету. Родитель также может выбрать ребенка, отчет для которого он хочет посмотреть.

#### Ученик и родитель
-	/diary – дневник. Можно выбрать неделю. Показываются все предметы на этой неделе, оценки, домашние задания. Родитель может выбирать ребенка, дневник которого он хочет посмотреть;
-	/reports – отчёты об оценках ученика за определенную четверть. Отображается количество оценок: пятерок, четверок, троек, двоек. Высчитывается средний балл по каждому предмету. Родитель также может выбрать ребенка, отчет для которого он хочет посмотреть.

## Использованные библиотеки и фреймворки
-	**Flask**
-	**SQLAlchemy** (работа с данной библиотекой осуществлялась через flask-sqlalchemy)
-	**jQuery** + **AJAX**
## Использованное программное обеспечение
-	**PyCharm 2018 Professional Edition**
-	**Adobe Photoshop CC**
## На каких языках написан OkayJournal?
-	**Python 3** - backend
- **JavaScript**, **HTML**, **CSS** - frontend
