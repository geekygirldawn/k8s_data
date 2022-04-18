# Kubernetes Owners Datasets
<a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-sa/4.0/88x31.png" /></a><br /><span xmlns:dct="http://purl.org/dc/terms/" href="http://purl.org/dc/dcmitype/Dataset" property="dct:title" rel="dct:type">These Kubernetes Owners Datasets</span> by <a xmlns:cc="http://creativecommons.org/ns#" href="https://github.com/geekygirldawn/k8s_data/datasets" property="cc:attributionName" rel="cc:attributionURL">Dawn Foster</a> are licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/">Creative Commons Attribution-ShareAlike 4.0 International License</a>.
The goal is to allow people to use these datasets freely with attribution.

## Datasets available

**owners_data_2022-04-18.csv** 

Uses only the OWNERS files found in sigs.yaml plus the OWNERS_ALIASES file containing leads. For details, see:
https://github.com/kubernetes/community/blob/master/sigs.yaml
https://github.com/kubernetes/kubernetes/blob/master/OWNERS_ALIASES

Caveat: sigs.yaml is always a little out of date. See this [GitHub issue](https://github.com/kubernetes/community/issues/6307) for more details.

**owners_data_2022-04-18_xtra_owners.csv**

Contains the above data plus extra OWNERS files found using the Github search API generated with get_more_owners.py in the project using the kubernetes GitHub org.

Caveat: This probably includes OWNERS files that are in deprecated bits of the code that are no longer in use, and the GitHub search API is a bit flaky, so it's also likely missing some OWNERS files.

## Generating updates

You can run the owners_details.py program in this repo to generate your own, up to date dataset.

