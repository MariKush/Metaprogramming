






package p;

@Annotation ( param1 = "value1", param2 = "value2" )
@SuppressWarnings( {"ALL"} )
public class Foo< T extends Bar & Abba, U > {

	int[] X = new int[]{ 1, 3, 5, 6, 7, 87, 1213, 2 };

	int[] empty = new int[]{};

	public void foo ( int x, int y ){
		Runnable r = ( ) -> {
		};
		Runnable r1 = this::bar;
		for ( int i = 0; i < x; i++ ) {
			y += (y ^ 0x123) << 2;
		}
		do {
			try ( MyResource r1 = getResource ( ); MyResource r2 = null ) {
				if ( 0 < x && x < 10 ) {
					while ( x != y ) {
						x = f ( x * 3 + 5 );
					}
				} else {
					synchronized ( this ) {
						switch ( a ) {
							case 0:
							case 1:
								doCase0 ( );
								break;
							case 2:
							case 3: {
								return;
							}
							default:
								doDefault ( );
							}
						}
					}
				} catch ( MyException e ) {
			} finally {
				int[] arr = ( int[] ) g ( y );
				x = y >= 0 ? arr[ y ] : -1;
				Map< String, String > sMap = new HashMap< String, String >();
				Bar.< String, Integer > mess ( null );
			}
		} while ( true );
	}
	void bar ( ){
		{
			return;
		}
	}
}
class Bar {
	static< U, T > U mess ( T t ){
		return null;
	}
}
interface Abba{
}
class Test {
	public static void main ( String[] args ){

		int[] array = {51, 136, 387};

		for ( int i : array ) {
			System.out.println ( i );
		}
		if ( a < b ) {
			println ( a );

		}

	}
}

@Annotation1
@Annotation2
@Annotation3 ( param1 = "value1", param2 = "value2" )
@Annotation4
class Foo {
	@Annotation1
	@Annotation3 ( param1 = "value1", param2 = "value2" )
	public static void foo ( ){
	}
	@Annotation1
	@Annotation3 ( param1 = "value1", param2 = "value2" )
	public static int myFoo;
	public void method(@Annotation1 @Annotation3 ( param1 = "value1", param2 = "value2" )final int param) {
		@Annotation1
		@Annotation3 ( param1 = "value1", param2 = "value2" )
		final int localVariable;
	}
}