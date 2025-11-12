#!/usr/bin/env sh

REPO=`basename $(git rev-parse --show-toplevel)`
PR=`gh pr view --json number --jq '.number'`
PASS=`gcloud secrets versions access latest --secret grafana-ephemeral-admin-password --project rhiza-shared`
uvx grafana-weaver config add $REPO-$PR --server https://dev.shared.rhizaresearch.org/$REPO/$PR --user admin --password $PASS --org-id 1 --use-context
