# Help on class Cue in module threefive3.cue


```py3

class Cue(threefive3.base.SCTE35Base)
 |  Cue(data=None, packet_data=None)
 |  
 |  The threefive3.Cue class handles parsing
 |  SCTE 35 message strings.
 |  Example usage:
 |  
 |  >>>> import threefive3
 |  >>>> Base64 = "/DAvAAAAAAAA///wBQb+dGKQoAAZAhdDVUVJSAAAjn+fCAgAAAAALKChijUCAKnMZ1g="
 |  >>>> cue = threefive3.Cue(Base64)
 |  >>>> cue.show()
 |  
 |  * A cue instance can be initialized with
 |   Base64, Bytes, Hex, Int, Json, Xml, or Xml+binary data.
 |  
 |  * Instance variables can be accessed via dot notation.
 |  
 |  >>>> cue.command
 |  {'command_length': 5, 'name': 'Time Signal', 'time_specified_flag': True,
 |  'pts_time': 21695.740089}
 |  
 |  >>>> cue.command.pts_time
 |  21695.740089
```
### SCTE-35 data comes in a variety of formats. threefive3 handles all of the SCTE-35 formats.

* base64
* bytes
* hex
* int
* json
* xml
* xml+ binary



### Decoding is easy. The Cue class auto-detects SCTE-35 input format. 

* Here I'm decoding SCTE-35 in base64

```py3
Python 3.9.16 (7.3.11+dfsg-2+deb12u3, Dec 30 2024, 22:36:23)
[PyPy 7.3.11 with GCC 12.2.0] on linux
Type "help", "copyright", "credits" or "license" for more information.

>>>> from threefive3 import Cue
>>>> data='/DAgAAAAAAAAAP/wDwUAAAABf//+AFJlwAABAAAAAMOOklg='
>>>> cue=Cue(data)
```
* Three lines of code and the data is decoded
* This is how you decode base64, bytes, hex, int , json xml or xmlbin SCTE-35 data, it all works the same way.

### Editing SCTE-35 is easy, just use dot naotation to access all SCTE-35 data.
* Everything is directly editable.
```py3
>>>> cue.command.break_duration
60.0
>>>> cue.command.break_duration=73
>>>> cue.command.break_duration
73
```

### output works like this 

* base64
```py3
>>>> cue.base64()

'/DAgAAAAAAAAAP/wDwUAAAABf//+AFJlwAABAAAAAMOOklg='

```
* bytes
```py3
>>>> cue.bytes()
b'\xfc0 \x00\x00\x00\x00\x00\x00\x00\xff\xf0\x0f\x05\x00\x00\x00\x01\x7f\xff\xfe\x00Re\xc0\x00\x01\x00\x00\x00\x00\xc3\x8e\x92X'
```

* int
```py3
>>>> cue.int()
1913741249324105789713965315611872444571137197654250805822733947388252170837252018776
```
* json
    * cue.json() returns json
    * cue.show() pretty prints it.
```py3
>>>> cue.show()
{
    "info_section": {
        "table_id": "0xfc",
        "section_syntax_indicator": false,
        "private": false,
        "sap_type": "0x03",
        "sap_details": "No Sap Type",
        "section_length": 32,
        "protocol_version": 0,
        "encrypted_packet": false,
        "encryption_algorithm": 0,
        "pts_adjustment": 0.0,
        "cw_index": "0x00",
        "tier": "0x0fff",
        "splice_command_length": 15,
        "splice_command_type": 5,
        "descriptor_loop_length": 0,
        "crc": "0xc38e9258"
    },
    "command": {
        "command_length": 15,
        "command_type": 5,
        "name": "Splice Insert",
        "break_auto_return": true,
        "break_duration": 60.0,
        "splice_event_id": 1,
        "splice_event_cancel_indicator": false,
        "out_of_network_indicator": true,
        "program_splice_flag": true,
        "duration_flag": true,
        "splice_immediate_flag": true,
        "event_id_compliance_flag": true,
        "unique_program_id": 1,
        "avail_num": 0,
        "avails_expected": 0
    },
    "descriptors": []
}
```

* hex
```py3
>>>> cue.hex()
'0xfc302000000000000000fff00f05000000017ffffe005265c0000100000000c38e9258'
```
* xml
```py3
>>>> cue.xml()
<scte35:SpliceInfoSection xmlns:scte35="https://scte.org/schemas/35"  ptsAdjustment="0" protocolVersion="0" sapType="3" tier="4095">
   <scte35:SpliceInsert spliceEventId="1" spliceEventCancelIndicator="false" spliceImmediateFlag="true" eventIdComplianceFlag="true" availNum="0" availsExpected="0" outOfNetworkIndicator="true" uniqueProgramId="1">
      <scte35:BreakDuration autoReturn="true" duration="5400000"/>
   </scte35:SpliceInsert>
</scte35:SpliceInfoSection>
```
* xml+binary
```py3
>>>> cue.xmlbin()
<scte35:Signal xmlns:scte35="https://scte.org/schemas/35">
   <scte35:Binary>/DAgAAAAAAAAAP/wDwUAAAABf//+AFJlwAABAAAAAMOOklg=</scte35:Binary>
</scte35:Signal>
```


