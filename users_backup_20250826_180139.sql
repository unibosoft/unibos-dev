--
-- PostgreSQL database dump
--

\restrict ph19ObAZgPq6ZBNgJG5xHOXyvIa8QlXC7ysUELsfJLgE1GYSUIYJxkfMOdZvHsy

-- Dumped from database version 14.18 (Homebrew)
-- Dumped by pg_dump version 14.19 (Homebrew)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: unibos_user
--

COPY public.users (password, last_login, is_superuser, username, first_name, last_name, is_staff, is_active, date_joined, id, email, phone_number, bio, avatar, date_of_birth, country, city, user_timezone, language, theme, notifications_enabled, email_notifications, is_verified, verification_token, last_password_change, require_password_change, last_activity, login_count, created_at, updated_at) FROM stdin;
pbkdf2_sha256$720000$GAeKTx6kvEZM4MgKHUNXYN$cuDqNYPs2BUI8CYNzbBZ4xRhuvdOw2J/nTQGAazhlpY=	\N	t	admin	Admin	User	t	t	2025-08-20 02:06:50.5348+03	3cc8d645-5913-4ec5-8a19-ca02041e2677	admin@unibos.com		Admin User - UNIBOS User		\N	TR	Istanbul	Europe/Istanbul	tr	dark	t	t	t		2025-08-20 02:06:50.534801+03	f	\N	0	2025-08-20 02:06:50.534913+03	2025-08-20 02:06:50.534915+03
pbkdf2_sha256$720000$KnaGhP7hukPDCGvk7ptLSR$uS8AG1oB1Fn914of26bYh3jhbcOWjSnDsygcPW/4us8=	\N	f	ahmet	Ahmet	Yılmaz	f	t	2025-08-20 02:06:50.535621+03	9eb0fe3a-43b4-43b7-af38-d50523949bcc	ahmet@unibos.com		Ahmet Yılmaz - UNIBOS User		\N	TR	Istanbul	Europe/Istanbul	tr	dark	t	t	t		2025-08-20 02:06:50.535622+03	f	\N	0	2025-08-20 02:06:50.593644+03	2025-08-20 02:06:50.593651+03
pbkdf2_sha256$720000$ntsSXLxE91Ou4F0vZFF9DW$JkTFNcWK18gFQsE4ahKzRlesa0XOrJcbCWHDL1wsdjE=	\N	f	mehmet	Mehmet	Demir	f	t	2025-08-20 02:06:50.59981+03	89e04e25-6d1a-4740-80c8-22cd38c21949	mehmet@unibos.com		Mehmet Demir - UNIBOS User		\N	TR	Istanbul	Europe/Istanbul	tr	dark	t	t	t		2025-08-20 02:06:50.599811+03	f	\N	0	2025-08-20 02:06:50.658267+03	2025-08-20 02:06:50.658274+03
pbkdf2_sha256$720000$bOxbuwSCdih0jlu5mD6V5N$olGKCMVRjDWC6qNyGWxAZ/+rHzi1MMv6nvO1a5A2sbg=	\N	f	ayse	Ayşe	Kaya	f	t	2025-08-20 02:06:50.659544+03	71c5a40e-6cd7-4a58-bd08-1989d85ee102	ayse@unibos.com		Ayşe Kaya - UNIBOS User		\N	TR	Istanbul	Europe/Istanbul	tr	dark	t	t	t		2025-08-20 02:06:50.659545+03	f	\N	0	2025-08-20 02:06:50.718122+03	2025-08-20 02:06:50.718127+03
pbkdf2_sha256$720000$xB1BHMsKG9Mv0yskEE5AUQ$yjgmLQ+YC8QJBDSUpulIrynw1RZGUT+UERZXCgJJ7Ks=	\N	f	fatma	Fatma	Öztürk	f	t	2025-08-20 02:06:50.719713+03	a6fe44d3-8628-424b-bd32-d14ef7683951	fatma@unibos.com		Fatma Öztürk - UNIBOS User		\N	TR	Istanbul	Europe/Istanbul	tr	dark	t	t	t		2025-08-20 02:06:50.719715+03	f	\N	0	2025-08-20 02:06:50.778002+03	2025-08-20 02:06:50.778006+03
pbkdf2_sha256$720000$0UAVr7aoCLkyNYDp3MLGAm$VBPc2xKdLmWK+h1RP9bW3nKxnu43Ebao5Prae9qHkM0=	\N	f	ali	Ali	Çelik	t	t	2025-08-20 02:06:50.779473+03	35e3be19-9658-44da-a001-a4d5f59e0fc7	ali@unibos.com		Ali Çelik - UNIBOS User		\N	TR	Istanbul	Europe/Istanbul	tr	dark	t	t	t		2025-08-20 02:06:50.779474+03	f	\N	0	2025-08-20 02:06:50.837942+03	2025-08-20 02:06:50.837945+03
pbkdf2_sha256$720000$SeiStJwp7iF9hFDKhHo64w$IF4hZEWJ8Y3Fknp8Mu6SYSdzYKt/QBIrO0xnfGyR71Y=	\N	f	zeynep	Zeynep	Arslan	f	t	2025-08-20 02:06:50.839205+03	8784f50b-9dcd-4142-9faf-c583dbd9d3ad	zeynep@unibos.com		Zeynep Arslan - UNIBOS User		\N	TR	Istanbul	Europe/Istanbul	tr	dark	t	t	t		2025-08-20 02:06:50.839206+03	f	\N	0	2025-08-20 02:06:50.897053+03	2025-08-20 02:06:50.897056+03
pbkdf2_sha256$720000$OnZNp5tcCOkE6mfqwF6ISd$hy34elGaAzgargRYKFxXDU1SZc5t7Hlvx6EelQ06BNQ=	\N	f	mustafa	Mustafa	Şahin	t	t	2025-08-20 02:06:50.898273+03	c006dcf9-6353-474e-932d-59cd7d3c3785	mustafa@unibos.com		Mustafa Şahin - UNIBOS User		\N	TR	Istanbul	Europe/Istanbul	tr	dark	t	t	t		2025-08-20 02:06:50.898274+03	f	\N	0	2025-08-20 02:06:50.957586+03	2025-08-20 02:06:50.957589+03
pbkdf2_sha256$720000$4cPjyUT2Zp2JlyPW5HcAuN$iijGL632NmuLk16CJtSXctSKg4gS9n0jpFbpGscYRk0=	\N	f	elif	Elif	Yıldız	f	t	2025-08-20 02:06:50.959006+03	9a81c6e3-2acb-47e9-9e21-fcb2a9ad57ec	elif@unibos.com		Elif Yıldız - UNIBOS User		\N	TR	Istanbul	Europe/Istanbul	tr	dark	t	t	t		2025-08-20 02:06:50.959006+03	f	\N	0	2025-08-20 02:06:51.017341+03	2025-08-20 02:06:51.017343+03
pbkdf2_sha256$720000$seJPZoz7tsiY3tBPWovyuO$LhxhUgHlcOH5bqi6DVDKBf9r8XFEgAnV3dRg6VqTXho=	2025-08-26 17:52:00.170784+03	t	berkhatirli	Berk	Hatırlı	t	t	2025-08-20 02:06:50.533142+03	a796dee1-b75e-4284-b44d-d7ba7eb1d8ca	berk@unibos.com		Berk Hatırlı - UNIBOS User		\N	TR	Istanbul	Europe/Istanbul	tr	dark	t	t	t		2025-08-20 02:06:50.533145+03	f	2025-08-26 17:52:00.171897+03	32	2025-08-20 02:06:50.533397+03	2025-08-20 02:15:07.671417+03
\.


--
-- PostgreSQL database dump complete
--

\unrestrict ph19ObAZgPq6ZBNgJG5xHOXyvIa8QlXC7ysUELsfJLgE1GYSUIYJxkfMOdZvHsy

