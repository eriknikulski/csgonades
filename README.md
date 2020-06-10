Create a folder called ```fonts``` and put a folder with the open sans font in it.
You can find it here [https://fonts.google.com/specimen/Open+Sans](https://fonts.google.com/specimen/Open+Sans).

To create a pdf for inferno use:
```python
python3 main.py inferno
```

Create for one side only with the optional argument ```--side=?``` and place ether ```t``` or ```ct``` at ```?```.

Create only for some nades with the optional argument ```--nades ``` and put after that a space separated list of the nades you want.
Where a nade is part of ```['smokes', 'mollies', 'flashes', 'hes']```.


Example: 
```python
python3 main.pdf inferno --side=t --nades smokes flashes
```