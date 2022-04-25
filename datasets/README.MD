# Datasets
<a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-sa/4.0/88x31.png" /></a><br /><span xmlns:dct="http://purl.org/dc/terms/" href="http://purl.org/dc/dcmitype/Dataset" property="dct:title" rel="dct:type">These Datasets</span> by <a xmlns:cc="http://creativecommons.org/ns#" href="https://github.com/geekygirldawn/k8s_data/tree/main/datasets" property="cc:attributionName" rel="cc:attributionURL">Dawn Foster</a> are licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/">Creative Commons Attribution-ShareAlike 4.0 International License</a>.
The goal is to allow people to use these datasets freely with attribution.

If you find any issues with these datasets, please feel free to file an issue in this GitHub repo. Please do not send PRs against the csv files, since those are auto generated using scripts.

## Kubernetes OWNERS Datasets

These datasets use Kubernetes OWNERS files along with [CNCF Affiliation data](https://github.com/cncf/gitdm) to gather information about leads, approvers, and reviewers by SIG / Subproject (where available) and including their corporate affiliations for most people. The dataset also includes the OWNERS file where the information was obtained to allow for data validation.

**[owners_data_2022-04-18.csv](owners_data_2022-04-18.csv)** 

Uses only the OWNERS files found in sigs.yaml plus the OWNERS_ALIASES file containing leads. For details, see:
https://github.com/kubernetes/community/blob/master/sigs.yaml
https://github.com/kubernetes/kubernetes/blob/master/OWNERS_ALIASES

Caveat: sigs.yaml is always a little out of date. See this [GitHub issue](https://github.com/kubernetes/community/issues/6307) for more details.

**[owners_data_2022-04-18_xtra_owners.csv](owners_data_2022-04-18_xtra_owners.csv)**

Contains the above data plus extra OWNERS files found using the Github search API generated with `get_more_owners.py` in this repo using the kubernetes GitHub org.

Caveat: This probably includes OWNERS files that are in deprecated bits of the code that are no longer in use, and the GitHub search API is a bit flaky, so it's also likely missing some OWNERS files.

### Generating updates

You can run the `owners_details.py` program in this repo to generate your own, up to date dataset.

## Istio Leadership Dataset

This dataset uses the Istio [teams.yaml](https://raw.githubusercontent.com/istio/community/master/org/teams.yaml) file along with [CNCF Affiliation data](https://github.com/cncf/gitdm) and the GitHub API for emails listed on GitHub profiles to gather information about maintainers and other leadership positions.

**[owners_data_istio_2022-04-25.csv](owners_data_istio_2022-04-25.csv)**

There is a [Jupyter Notebook](Istio_Leadership_Analysis.ipynb) with some basic analysis using this Istio dataset.

### Generating updates

You can run the `istio_owners.py` program in this repo to generate your own, up to date dataset.
