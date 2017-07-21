
update_deploy:
	git checkout deploy
	git rebase master
	git checkout master

deploy:
	git push heroku deploy:master
