# Getting started with Grafana weaver and Sheerwater

In sheerwater dashboards are stored in version control. There are source dashboards that are then built in json which is automatically deployed on either to production (when merged into main) or into an ephemeral environment associated with a Pull Request.

Grafana weaver is a tool which copies the current state of Grafana from the target instance to your local machine and deploys your changes back to the cloud.

So the general flow would be:

(1) Make a Pull Request
(2) Tag that pull request with "PR-ENV" so that it starts an ephemeral grafana instance for you
(3) Edit that your dashboards in whatever way you want
(4) If you edited them in the cloud use grafana weaver to copy your changes to your machine and commit/push those changes
(5) If you edited them locally use grafana weaver to deploy them to the cloud and view them.
(6) People review the PR and it deploys to main

## Installing dependencies

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
brew install gh
curl https://sdk.cloud.google.com | bash
gcloud auth login
gcloud auth application-default login
```

## Creating A Pull Request and Tagging it

```sh
git checkout -b <my-feature-branch>
gh pr create --title "Testing grafana dashboards"
gh pr edit --add-label "PR-env"
./grafana-weaver-bootstrap.sh
```
You should now be able to see a comment in your PR with a link to the ephemeral grafana

## Make Changes in the cloud and download them

Make some changes to the ephemeral dashboards and download them

```sh
uvx grafana-weaver download
```

## Make changes locally and push them to the cloud

Edit one of the dashboards/src/jsonnet files and run

```sh
uvx grafana-weaver upload
```

## Using tags to share resources across dashboards and panels

In grafana cloud tag one of the edittable boxes with "EXTERNAL" in a comment in the text box then run

```sh
uvx grafana-weaver download
```

Now you should have an assets folder with the file you made that is editable in dashboards/src/assets. You can edit that file and re-upload it

```sh
uvx grafana-weaver upload
```
