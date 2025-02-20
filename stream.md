# threefive3.Stream class

```js

Help on class Stream in module threefive3.stream:

class Stream(builtins.object)
 |  Stream(tsdata, show_null=True)
 |  
 |  Stream class for parsing MPEG-TS data.
 |  
 |  Methods defined here:
 |  
 |  __init__(self, tsdata, show_null=True)
 |      tsdata is an file or http/https, or multicast, or UDP unicast URI.
 |      set show_null=False to exclude Splice Nulls
 |      
 |      Use like...
 |      
 |      from threefive3 import Stream
 |      strm = Stream("vid.ts",show_null=False)
 |      strm.decode()
 |  
 |  
```
# Methods
* [\_\_init__](#streaminitself-tsdata-show_nulltrue)
* [decode](#streamdecodeself-funcshow_cue)
* [decode_next](#streamdecode_nextself)
* [decode_pids](#streamdecode_pidsself-scte35_pids-funcshow_cue)
* [proxy](#streamproxyself-funcshow_cue)
* [show](#streamshowself)


## Stream.\_\_init__(self, tsdata, show_null=True)
```js
 __init__(self, tsdata, show_null=True)
 |      tsdata is an file or http/https, or multicast, or UDP unicast URI.
 |
 |       set show_null=False to exclude Splice Nulls
```
## Stream.decode(self, func=show_cue)
 ```js
 |  decode(self,func=show_cue)
 |      Stream.decode reads self.tsdata to find SCTE35 packets.
 |      func can be set to a custom function that accepts
 |      a threefive3.Cue instance as it's only argument.
 ```
Example:
```py3
from threefive3 import Stream
strm =Stream("https://futzu.com/xaa.ts")
strm.decode()
```
* The decode method allows passing in a function to run when SCTE-35 data is found.
* The function follows the interface
```py3
    func(cue)
```
* the arg `cue` is a threefive3.Cue instance. When the Stream class finds SCTE-35 data, it loads it into a Cue instance and calls func.
* The default is show_cue, it prints the cue data to sterr, aka 2.
* Here's an example that encodes the SCTE-35 Cue to base64
Example from the threefive3 cli tool:
```py3
from threefive3 import Stream

def base64_out(cue):
    """
    print SCTE-35 from mpegts as base64
    """
    print2(cue.base64())

strm =Stream("https://futzu.com/xaa.ts")
strm.decode(func=base64_out)
```
* output
```js
/DAvAAAAAAAA///wFAVAAAT2f+/+eMpEWX4A9zFAAAEL/wAKAAhDVUVJAAAACwRZmfY=
/DAqAAAAAAAA///wDwUAAAASf0/+dihKegABEv8ACgAIQ1VFSQAAABIe1kvb
/DAqAAAAAAAA///wDwUAAAASf0/+dihKegABEv8ACgAIQ1VFSQAAABIe1kvb
/DAqAAAAAAAA///wDwUAAAASf0/+dihKegABEv8ACgAIQ1VFSQAAABIe1kvb
/DAvAAAAAAAA///wFAUAAAAWf+/+eqdoEv4Ag9YAAAoI/wAKAAhDVUVJAAAACEMQGFI=
/DAvAAAAAAAA///wFAUAAAAXf+/+eq+lcv4Ae5igAAEI/wAKAAhDVUVJAAAACEre6z4=
/DAqAAAAAAAA///wDwVAAAT2f0/+ecF1mQABC/8ACgAIQ1VFSQAAAAsuZVlR
```
## Stream.decode_next(self)

```py3
 |  decode_next(self)
 |      Stream.decode_next returns the next
 |      SCTE35 cue as a threefive3.Cue instance.
 |
```
## Stream.decode_pids(self, scte35_pids=[], func=show_cue)
```py3
 |  decode_pids(self, scte35_pids=[], func=show_cue)
 |      Stream.decode_pids takes a list of SCTE-35 Pids parse
 |      and an optional call back function to run when a Cue is found.
 |      if scte35_pids is not set, all threefive3 pids will be parsed.
 |
```
## Stream.proxy(self, func=show_cue)
```py3
 |  proxy(self, func=show_cue)
 |      Stream.decode_proxy writes all ts packets are written to stdout
 |      for piping into another program like mplayer.
 |      SCTE-35 cues are print2`ed to stderr.
 |
```
## Stream.show(self)
```py3
 |  show(self)
 |      displays streams that will be
 |      parsed for SCTE-35.
 |  
```

