# ROCKS updating

## Outdated packages

When packages in OCI are marked as outdated **without** changes in packaged application (no major/minor release), i.e. no changes in `Dockerfile` or release tag, and **without** changes in the base image.

For each affected tag, do:

```mermaid
flowchart TD
    id001([start]) --> id002[LP: request rebuild]
    id002 --> id003[LP: wait until uploaded\nto public registries]
    id003 --> id004[oci unit test]
    id004 --> id005[tag on public\nregistries]
    id005 --> id006[reply security e-mail]
    id006 --> id099([end])
```

## Update the application version (deb-based)

When the packaged application has a version bump, e.g. `redis-6.0 -> redis-6.1`. Each application have it's own versioning rule, in the sense to when it makes sense to bump the tag or not given a change in major or minor release.

```mermaid
flowchart TD
    id001([start]) --> id002[LP: clone OCI repo]
    id002 --> id003[Create new branch\nfollowing convention]
    id003 --> id004{any code\nchange\nneeded}
    id004 -- no --> id005[build  test locally]
    id004 -- yes --> id006[make changes]
    id006 --> id005
    id005 --> id007{Tests passing?}
    id007 -- yes --> id008[file MP]
    id007 -- no --> id006
    id008 --> id009[get reviewed]
    id009 --> id110[merge]
    id110 --> id010[LP: create/edit recipe]
    id010 --> id011[LP: request build]
    id011 --> id012[LP: wait until uploaded\nto public registries]
    id012 --> id013[oci unit test]
    id013 --> id014[tag on public\nregistries]
    id014 --> id099([end])
```

## Update the application version (snap-based)

### Special notes
- kafka (and other java-based) depends on gradle plugin to build, which is deprecated
- security notification comes only for the snap package (not for the ROCK)
- kafka snap repo has a `rock` and a `main` branch, which publish to respective store channels

```mermaid
flowchart TD
    id001([start]) --> id002[LP: clone SNAP repo]
    id002 --> id003[Create new branch\nfollowing convention]
    id003 --> id004{any code\nchange\nneeded}
    id004 -- no --> id005[build  test locally]
    id004 -- yes --> id006[make changes]
    id006 --> id005
    id005 --> id007{Tests passing?}
    id007 -- yes --> id008[file MP]
    id007 -- no --> id006
    id008 --> id009[get reviewed]
    id009 --> id010[merge]
    id010 --> id011[LP: request snap build]
    id011 --> id012[LP: wait until uploaded\nto snapcraft.io]
    id012 --> id013[LP: request OCI build]
    id013 --> id014[LP: wait until uploaded\nto public registries]
    id014 --> id015[oci unit test]
    id015 --> id016[tag on public\nregistries]
    id016 --> id099([end])
```
