from matplotlib import cm
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import matplotlib.patheffects as PathEffects
from mplstyles import cmap as colormap
import types
import numpy as np
import scipy.ndimage

def contour_image(x,y,Z,
					cmap=None,
					vmax=None,
					vmin=None,
					interpolation='nearest',
					contour_smoothing=0,
					label=False,
					clegendlabels=[],
					outline=None,
					cguides=False,
					cguide_tomax=True,
					cguide_stride=1,
					contour_opts={},
					label_opts={},
					imshow_opts={},
					cguide_opts={}):
	ax = plt.gca()

	x_delta = float((x[-1]-x[0]))/(len(x)-1)/2.
	y_delta = float((y[-1]-y[0]))/(len(y)-1)/2.

	extent=(x[0],x[-1],y[0],y[-1])

	extent_delta = (x[0]-x_delta,x[-1]+x_delta,y[0]-y_delta,y[-1]+y_delta)

	ax.set_xlim(x[0],x[-1])
	ax.set_ylim(y[0],y[-1])

	aspect=(x[-1]-x[0])/(y[-1]-y[0])

	if cmap is None:
		cmap = colormap.reverse(cm.Blues)

	Z = Z.transpose()

	if vmin is None:
		vmin = np.min(Z)
	if vmax is None:
		vmax = np.max(Z)

	#plt.contourf(X,Y,self.pdata,interpolation=interpolation)
	cs = ax.imshow(Z,interpolation=interpolation,origin='lower',aspect='auto',extent=extent_delta,cmap=cmap,vmax=vmax,vmin=vmin, **imshow_opts)

	# Draw contours
	if contour_smoothing != 0:
		Z = scipy.ndimage.zoom(Z, contour_smoothing)
	X, Y = np.meshgrid(x, y)
	CS = ax.contour(X, Y, Z, extent=extent, origin='lower', vmax=vmax,vmin=vmin, **contour_opts )

	if outline is True:
		def outline(cvalue, vmin=0, vmax=1):
			color = CS.cmap(float(cvalue - vmin) / (vmax-vmin))
			if np.sqrt(np.sum(np.array(color[:3])**2)) <= 0.5:
				return (1,1,1,0.2)
			return (0,0,0,0.2)
	if type(outline) is types.FunctionType or isinstance(outline, colors.Colormap):
		outline = [outline(c, vmin=vmin, vmax=vmax) for c in CS.cvalues]
	elif type(outline) is list:
		pass
	elif outline is None:
		pass
	else:
		outline = [outline]*len(CS.cvalues)

	if outline is not None:
		for i,collection in enumerate(CS.collections):
			plt.setp(collection, path_effects=[
				PathEffects.withStroke(linewidth=3, foreground=outline[i])])

	# Label contours
	if label:
		clbls = ax.clabel(CS, **label_opts)
		if outline is not None:
			for i,clbl in enumerate(clbls):
				plt.setp(clbl, path_effects=[
						PathEffects.withStroke(linewidth=1.5, foreground=outline[np.argmin(np.abs(CS.cvalues-float(clbl.get_text())))])])

	# Draw guides on specified contours
	if cguides is True:
		cguides = CS.cvalues
	if cguides is not False:
		decorate_contour_segments(CS, cguides, cguide_stride, vmin, vmax, cguide_opts, tomax=cguide_tomax, outline=outline, aspect=aspect)

	# Show contours in legend if desired
	if len(clegendlabels) > 0:
		for i in range(len(clegendlabels)):
			CS.collections[i].set_label(clegendlabels[i])
		#ax.legend()

	return cs, CS

def decorate_contour_segments(CS, cvalues, stride=1, vmin=0, vmax=1, options={}, tomax=True, outline=None, aspect=1):
	for i,value in enumerate(cvalues):
		options['color'] = CS.cmap(float(value - vmin) / (vmax-vmin))
		for index in np.where(np.isclose(value, CS.cvalues))[0]:
			for segment in CS.collections[index].get_segments():#for segment in CS.allsegs[index]:
				decorate_contour_segment(segment, stride=stride, options=options, tomax=tomax, labelled=hasattr(CS,'cl'), outline=outline[i] if outline is not None else None, aspect=aspect)

def decorate_contour_segment(data, stride=1, options={}, tomax=True, labelled=False, outline=None, aspect=1):
	default_options = {'scale': 0.2,
			'scale_units': 'dots',
			'headaxislength': 2,
			'headlength': 2,
			'headwidth': 2,
			'minshaft': 1,
			'units': 'dots',
			#'angles': 'xy',
			'edgecolor': outline,
			'linewidth': 0 if outline is None else 0.2
		}
	default_options.update(options)

	x = data[::stride,0]
	y = data[::stride,1]

	sign = 1 if tomax else -1
	dx = -sign*np.diff(y)*aspect
	dy = sign*np.diff(x)
	l = np.sqrt(dx**2+dy**2)
	dx /= l
	dy /= l

	x = 0.5*(x+np.roll(x,-1))
	y = 0.5*(y+np.roll(y,-1))

	if labelled:
		x,y,dx,dy = x[1:-2], y[1:-2], dx[1:-1], dy[1:-1]
	else:
		x,y = x[:-1], y[:-1]

	plt.quiver(x, y, dx, dy, **default_options)